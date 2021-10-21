package gossh_python_go

// #cgo pkg-config: python2
// #include <Python.h>
import "C"

// releaseGIL releases (unlocks) the Python GIL
func releaseGIL() *C.PyThreadState {
	var tState *C.PyThreadState

	tState = C.PyEval_SaveThread()

	return tState
}

// reacquireGIL reacquires (locks) the Python GIL
func reacquireGIL(tState *C.PyThreadState) {
	if tState == nil {
		return
	}

	C.PyEval_RestoreThread(tState)
}
