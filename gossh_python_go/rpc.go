package gossh_python_go

import (
	"fmt"
	"log"
	"runtime/debug"
	"sync"
	"time"
)

var sessionMutex sync.Mutex
var sessions map[uint64]*session
var lastSessionID uint64

func init() {
	sessions = make(map[uint64]*session)

	time.Sleep(time.Second) // give the Python side a little time to settle
}

// this is used to ensure the Go runtime keeps operating in the event of strange errors
func handlePanic(extra string, sessionID uint64, s *session, err error) {
	log.Printf(
		fmt.Sprintf(
			"handlePanic() for %v()\n\tSessionID: %v\n\tClient: %+v\n\tSession: %+v\n\tError: %v\n\nStack trace follows:\n\n%v",
			extra,
			sessionID,
			s.client,
			s.session,
			err,
			string(debug.Stack()),
		),
	)
}

// NewRPCSession creates a new session and returns the sessionID
func NewRPCSession(hostname, username, password string, port, timeout int) uint64 {
	if !GetPyPy() {
		tState := releaseGIL()
		defer reacquireGIL(tState)
	}

	session := newSession(
		hostname,
		username,
		password,
		port,
		timeout,
	)

	sessionMutex.Lock()
	sessionID := lastSessionID
	lastSessionID++
	sessions[sessionID] = &session
	sessionMutex.Unlock()

	return sessionID
}

// RPCConnect connects
func RPCConnect(sessionID uint64) error {
	if !GetPyPy() {
		tState := releaseGIL()
		defer reacquireGIL(tState)
	}

	var err error

	sessionMutex.Lock()
	val, ok := sessions[sessionID]
	sessionMutex.Unlock()

	// permit recovering from a panic but return the error
	defer func(s *session) {
		if r := recover(); r != nil {
			if handledError, _ := r.(error); handledError != nil {
				handlePanic("connect", sessionID, val, handledError)
				err = handledError
			}
		}
	}(val)

	if ok {
		err = val.connect()
	} else {
		err = fmt.Errorf("sessionID %v does not exist", sessionID)
	}

	return err
}

// RPCGetShell gets a shell
func RPCGetShell(sessionID uint64, terminal string, height, width int) error {
	if !GetPyPy() {
		tState := releaseGIL()
		defer reacquireGIL(tState)
	}

	var err error

	sessionMutex.Lock()
	val, ok := sessions[sessionID]
	sessionMutex.Unlock()

	// permit recovering from a panic but return the error
	defer func(s *session) {
		if r := recover(); r != nil {
			if handledError, _ := r.(error); handledError != nil {
				handlePanic("getShell", sessionID, val, handledError)
				err = handledError
			}
		}
	}(val)

	if ok {
		err = val.getShell(terminal, height, width)
	} else {
		err = fmt.Errorf("sessionID %v does not exist", sessionID)
	}

	return err
}

// RPCRead reads data
func RPCRead(sessionID uint64, size int) (string, error) {
	if !GetPyPy() {
		tState := releaseGIL()
		defer reacquireGIL(tState)
	}

	var err error

	sessionMutex.Lock()
	val, ok := sessions[sessionID]
	sessionMutex.Unlock()

	// permit recovering from a panic but return the error
	defer func(s *session) {
		if r := recover(); r != nil {
			if handledError, _ := r.(error); handledError != nil {
				handlePanic("read", sessionID, val, handledError)
				err = handledError
			}
		}
	}(val)

	data := ""

	if ok {
		data, err = val.read(size)
	} else {
		err = fmt.Errorf("sessionID %v does not exist", sessionID)
	}

	return data, err
}

// RPCWrite reads data
func RPCWrite(sessionID uint64, data string) error {
	if !GetPyPy() {
		tState := releaseGIL()
		defer reacquireGIL(tState)
	}

	var err error

	sessionMutex.Lock()
	val, ok := sessions[sessionID]
	sessionMutex.Unlock()

	// permit recovering from a panic but return the error
	defer func(s *session) {
		if r := recover(); r != nil {
			if handledError, _ := r.(error); handledError != nil {
				handlePanic("write", sessionID, val, handledError)
				err = handledError
			}
		}
	}(val)

	if ok {
		err = val.write(data)
	} else {
		err = fmt.Errorf("sessionID %v does not exist", sessionID)
	}

	return err
}

// RPCClose closes
func RPCClose(sessionID uint64) error {
	if !GetPyPy() {
		tState := releaseGIL()
		defer reacquireGIL(tState)
	}

	sessionMutex.Lock()
	val, ok := sessions[sessionID]
	sessionMutex.Unlock()

	if !ok {
		return nil
	}

	sessionMutex.Lock()
	delete(sessions, sessionID)
	sessionMutex.Unlock()

	// permit recovering from a panic silently (bury the error)
	defer func(s *session) {
		if r := recover(); r != nil {
			if handledError, _ := r.(error); handledError != nil {
				handlePanic("close", sessionID, val, handledError)
			}
		}
	}(val)

	return val.close()
}
