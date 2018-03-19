package gossh_python

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"sync"
	"time"

	"golang.org/x/crypto/ssh"
)

type sessionInterface interface {
	getConn() *ssh.Client
	getSession() *ssh.Session
	connect() error
	read() (string, error)
	write(string) error
	close() error
}

func handleReader(s *Session) {
	var writeErr error

	for {
		buf := make([]byte, 65536)
		n, readErr := s.stdout.Read(buf)

		if n > 0 {
			s.bufMutex.Lock()
			_, writeErr = s.buf.Write(buf)
			s.bufMutex.Unlock()
		}

		if readErr != nil {
			if readErr == io.EOF {
				continue
			}
			panic(readErr)
		}

		if writeErr != nil {
			panic(writeErr)
		}

		if n == 0 {
			continue
		}

		select {
		case <-s.ctx.Done():
			return
		default:
		}
	}
}

// Session holds all the state for an SSH session
type Session struct {
	conn      *ssh.Client
	session   *ssh.Session
	config    *ssh.ClientConfig
	connected bool
	addr      string
	stdout    io.Reader
	stdin     io.WriteCloser
	ctx       context.Context
	cancel    context.CancelFunc
	bufMutex  sync.Mutex
	buf       bytes.Buffer
}

// NewSession creates a new session
func NewSession(hostname, username, password string, port, timeout int) Session {
	return Session{
		conn:    nil,
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

// Connect connects
func (s *Session) Connect() error {
	if s.connected {
		return nil
	}

	conn, err := ssh.Dial("tcp", s.addr, s.config)
	if err != nil {
		return err
	}

	session, err := conn.NewSession()
	if err != nil {
		return err
	}

	s.conn = conn
	s.session = session
	s.connected = true

	s.ctx, s.cancel = context.WithCancel(context.Background())

	return nil
}

// GetShell gets a shell
func (s *Session) GetShell() error {
	var err error

	s.stdout, err = s.session.StdoutPipe()
	if err != nil {
		return err
	}

	s.stdin, err = s.session.StdinPipe()
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

	go handleReader(s)

	return nil
}

// Read reads
func (s *Session) Read(size int) (string, error) {
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

// Write writes
func (s *Session) Write(data string) error {
	_, err := s.stdin.Write([]byte(data))

	return err
}

// Close closes
func (s *Session) Close() error {
	if !s.connected {
		return nil
	}

	s.cancel()

	err := s.session.Close()
	if err != nil {
		return err
	}

	err = s.conn.Close()
	if err != nil {
		return err
	}

	return nil
}
