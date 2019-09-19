package gossh_python_go

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
				s.errMutex.Lock()
				s.err = fmt.Errorf("handleReader failed (connection now useless) because of STDIN: %v", writeErr)
				s.errMutex.Unlock()

				break
			}
		}

		if readErr != nil {
			s.errMutex.Lock()
			s.err = fmt.Errorf("handleReader failed (connection now useless) because of STDOUT: %v", readErr)
			s.errMutex.Unlock()

			break
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
	conn      net.Conn
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
	config := ssh.Config{}

	config.SetDefaults()

	config.Ciphers = append(
		config.Ciphers,
		"aes128-cbc",
		"3des-cbc",
		"aes256-cbc",
		"aes128-cbc",
		"twofish256-cbc",
		"twofish-cbc",
		"twofish128-cbc",
		"blowfish-cbc",
	)

	config.KeyExchanges = append(
		config.KeyExchanges,
		"diffie-hellman-group1-sha1",
	)

	return session{
		client:  nil,
		session: nil,
		config: &ssh.ClientConfig{
			Config: config,
			User:   username,
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
		Deadline:  time.Now().Add(s.config.Timeout),
	}

	conn, err := d.Dial("tcp", s.addr)
	if err != nil {
		return err
	}

	conn.SetDeadline(time.Now().Add(s.config.Timeout))
	c, chans, reqs, err := ssh.NewClientConn(conn, s.addr, s.config)
	if err != nil {
		return err
	}

	conn.SetDeadline(time.Now().Add(s.config.Timeout))
	client := ssh.NewClient(c, chans, reqs)

	conn.SetDeadline(time.Now().Add(s.config.Timeout))
	session, err := client.NewSession()
	if err != nil {
		return err
	}

	conn.SetDeadline(time.Time{})

	s.conn = conn
	s.client = client
	s.session = session
	s.connected = true

	s.errMutex.Lock()
	s.err = nil
	s.errMutex.Unlock()

	s.quit = make(chan struct{})

	return nil
}

func (s *session) getShell(terminal string, height, width int) error {
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

	s.conn.SetDeadline(time.Now().Add(s.config.Timeout))
	err = s.session.RequestPty(terminal, height, width, modes)
	if err != nil {
		return err
	}

	s.conn.SetDeadline(time.Now().Add(s.config.Timeout))
	err = s.session.Shell()
	if err != nil {
		return err
	}

	s.conn.SetDeadline(time.Time{})

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

	if s.conn != nil {
		s.conn.SetDeadline(time.Now().Add(s.config.Timeout))
		s.conn.Close()
		s.conn = nil
	}

	if s.quit != nil {
		close(s.quit)
	}

	s.wg.Wait()

	s.connected = false

	return nil
}
