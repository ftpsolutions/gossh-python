package gossh_python

import (
	"bytes"
	"fmt"
	"io"
	"net"
	"sync"
	"time"

	"golang.org/x/crypto/ssh"
)

func handleReader(s *session) {
	var writeErr error

	buf := make([]byte, 65536)

	s.wg.Add(1)

	for {
		n, readErr := io.ReadAtLeast(s.stdout, buf, 1)

		if n > 0 {
			s.bufMutex.Lock()
			_, writeErr = s.buf.Write(buf[0:n])
			s.bufMutex.Unlock()
			if writeErr != nil {
				if writeErr == io.EOF {
					break
				}

				s.errMutex.Lock()
				s.err = writeErr
				s.errMutex.Unlock()

				break
			}
		}

		if readErr != nil {
			if readErr == io.EOF {
				break
			}

			s.errMutex.Lock()
			s.err = readErr
			s.errMutex.Unlock()
		}

		if n == 0 {
			continue
		}

		select {
		case <-s.quit:
			break
		default:
		}
	}

	s.wg.Done()
}

type session struct {
	client    *ssh.Client
	session   *ssh.Session
	config    *ssh.ClientConfig
	connected bool
	addr      string
	stdout    io.Reader
	stdin     io.WriteCloser
	bufMutex  sync.Mutex
	buf       bytes.Buffer
	quit      chan struct{}
	wg        sync.WaitGroup
	errMutex  sync.Mutex
	err       error
}

func newSession(hostname, username, password string, port, timeout int) session {
	return session{
		client:  nil,
		session: nil,
		config: &ssh.ClientConfig{
			User: username,
			Auth: []ssh.AuthMethod{
				ssh.Password(password),
			},
			HostKeyCallback: ssh.InsecureIgnoreHostKey(),
			Timeout:         time.Second * time.Duration(timeout),
		},
		addr: fmt.Sprintf("%s:%d", hostname, port),
	}
}

func (s *session) connect() error {
	if s.connected {
		return nil
	}

	var err error

	d := net.Dialer{
		Timeout:   s.config.Timeout,
		KeepAlive: s.config.Timeout,
	}

	conn, err := d.Dial("tcp", s.addr)
	if err != nil {
		return err
	}

	c, chans, reqs, err := ssh.NewClientConn(conn, s.addr, s.config)
	if err != nil {
		return err
	}

	client := ssh.NewClient(c, chans, reqs)

	session, err := client.NewSession()
	if err != nil {
		return err
	}

	s.client = client
	s.session = session
	s.connected = true

	s.errMutex.Lock()
	s.err = nil
	s.errMutex.Unlock()

	s.quit = make(chan struct{})

	return nil
}

func (s *session) getShell() error {
	var err error

	stdout, err := s.session.StdoutPipe()
	if err != nil {
		return err
	}

	stdin, err := s.session.StdinPipe()
	if err != nil {
		return err
	}

	modes := ssh.TerminalModes{
		ssh.ECHO:          1,
		ssh.TTY_OP_ISPEED: 14400,
		ssh.TTY_OP_OSPEED: 14400,
	}

	err = s.session.RequestPty("vt100", 65536, 65536, modes)
	if err != nil {
		return err
	}

	err = s.session.Shell()
	if err != nil {
		return err
	}

	s.stdout = stdout
	s.stdin = stdin

	go handleReader(s)

	return nil
}

func (s *session) read(size int) (string, error) {
	s.errMutex.Lock()
	err := s.err
	s.errMutex.Unlock()

	if err != nil {
		return "", s.err
	}

	buf := make([]byte, size)

	s.bufMutex.Lock()
	n, err := s.buf.Read(buf)
	s.bufMutex.Unlock()

	if err != nil {
		if err == io.EOF {
			return "", nil
		}
		return "", err
	}

	if n == 0 {
		return "", nil
	}

	return string(buf), nil
}

func (s *session) write(data string) error {
	_, err := s.stdin.Write([]byte(data))

	return err
}

func (s *session) close() error {
	if s.session != nil {
		s.session.Close()
		s.session = nil
	}

	if s.client != nil {
		s.client.Close()
		s.client = nil
	}

	close(s.quit)

	s.wg.Wait()

	s.connected = false

	return nil
}
