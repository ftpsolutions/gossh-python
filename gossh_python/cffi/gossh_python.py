""""""
import collections
import os
import sys
import cffi as _cffi_backend

_PY3 = sys.version_info[0] == 3

ffi = _cffi_backend.FFI()
ffi.cdef("""
typedef signed char GoInt8;
typedef unsigned char GoUint8;
typedef short GoInt16;
typedef unsigned short GoUint16;
typedef int GoInt32;
typedef unsigned int GoUint32;
typedef long long GoInt64;
typedef size_t GoUintptr;
typedef unsigned long long GoUint64;
typedef GoInt64 GoInt;
typedef GoUint64 GoUint;
typedef float GoFloat32;
typedef double GoFloat64;
typedef struct { const char *p; GoInt n; } GoString;
typedef void *GoMap;
typedef void *GoChan;
typedef struct { void *t; void *v; } GoInterface;
typedef struct { void *data; GoInt len; GoInt cap; } GoSlice;
typedef struct { GoFloat32 real; GoFloat32 imag; } GoComplex64;
typedef struct { GoFloat64 real; GoFloat64 imag; } GoComplex128;

extern GoComplex64 _cgopy_GoComplex64(GoFloat32 p0, GoFloat32 p1);
extern GoComplex128 _cgopy_GoComplex128(GoFloat64 p0, GoFloat64 p1);
extern GoString _cgopy_GoString(char* p0);
extern char* _cgopy_CString(GoString p0);
extern void _cgopy_FreeCString(char* p0);
extern GoUint8 _cgopy_ErrorIsNil(GoInterface p0);
extern char* _cgopy_ErrorString(GoInterface p0);
extern void cgopy_incref(void* p0);
extern void cgopy_decref(void* p0);

extern void cgo_pkg_gossh_python_init();

extern GoUint64 cgo_func_gossh_python_NewRPCSession(GoString p0, GoString p1, GoString p2, GoInt p3, GoInt p4);
extern GoInterface cgo_func_gossh_python_RPCClose(GoUint64 p0);
extern GoInterface cgo_func_gossh_python_RPCConnect(GoUint64 p0);
extern GoInterface cgo_func_gossh_python_RPCGetShell(GoUint64 p0);
typedef struct { GoString r0; GoInterface r1; } cgo_func_gossh_python_RPCRead_return;
extern cgo_func_gossh_python_RPCRead_return cgo_func_gossh_python_RPCRead(GoUint64 p0, GoInt p1);
extern GoInterface cgo_func_gossh_python_RPCWrite(GoUint64 p0, GoString p1);
extern void cgo_func_gossh_python_SetPyPy();
extern GoUint8 cgo_func_gossh_python_GetPyPy();
""")

# python <--> cffi helper.
class _cffi_helper(object):

    here = os.path.dirname(os.path.abspath(__file__))
    lib = ffi.dlopen(os.path.join(here, "_gossh_python.so"))

    @staticmethod
    def cffi_cgopy_cnv_py2c_bool(o):
        return ffi.cast('_Bool', o)

    @staticmethod
    def cffi_cgopy_cnv_py2c_complex64(o):
        real = o.real
        imag = o.imag
        complex64 = _cffi_helper.lib._cgopy_GoComplex64(real, imag)
        return complex64

    @staticmethod
    def cffi_cgopy_cnv_py2c_complex128(o):
        real = o.real
        imag = o.imag
        complex128 = _cffi_helper.lib._cgopy_GoComplex128(real, imag)
        return complex128

    @staticmethod
    def cffi_cgopy_cnv_py2c_string(o):
        if _PY3:
            o = o.encode('ascii')
        s = ffi.new("char[]", o)
        return _cffi_helper.lib._cgopy_GoString(s)

    @staticmethod
    def cffi_cgopy_cnv_py2c_int(o):
        return ffi.cast('int', o)

    @staticmethod
    def cffi_cgopy_cnv_py2c_float32(o):
        return ffi.cast('float', o)

    @staticmethod
    def cffi_cgopy_cnv_py2c_float64(o):
        return ffi.cast('double', o)

    @staticmethod
    def cffi_cgopy_cnv_py2c_uint(o):
        return ffi.cast('uint', o)

    @staticmethod
    def cffi_cgopy_cnv_c2py_bool(c):
        return bool(c)

    @staticmethod
    def cffi_cgopy_cnv_c2py_complex64(c):
         return complex(c.real, c.imag)

    @staticmethod
    def cffi_cgopy_cnv_c2py_complex128(c):
         return complex(c.real, c.imag)

    @staticmethod
    def cffi_cgopy_cnv_c2py_string(c):
        s = _cffi_helper.lib._cgopy_CString(c)
        pystr = ffi.string(s)
        _cffi_helper.lib._cgopy_FreeCString(s)
        if _PY3:
            pystr = pystr.decode('utf8')
        return pystr

    @staticmethod
    def cffi_cgopy_cnv_c2py_errstring(c):
        s = _cffi_helper.lib._cgopy_ErrorString(c)
        pystr = ffi.string(s)
        _cffi_helper.lib._cgopy_FreeCString(s)
        if _PY3:
            pystr = pystr.decode('utf8')
        return pystr

    @staticmethod
    def cffi_cgopy_cnv_c2py_int(c):
        return int(c)

    @staticmethod
    def cffi_cgopy_cnv_c2py_float32(c):
        return float(c)

    @staticmethod
    def cffi_cgopy_cnv_c2py_float64(c):
        return float(c)

    @staticmethod
    def cffi_cgopy_cnv_c2py_uint(c):
        return int(c)

# make sure Cgo is loaded and initialized
_cffi_helper.lib.cgo_pkg_gossh_python_init()

# pythonization of: gossh_python.NewRPCSession 
def NewRPCSession(hostname, username, password, port, timeout):
    """NewRPCSession(str hostname, str username, str password, int port, int timeout) long\n\nNewRPCSession creates a new session and returns the sessionID\n"""
    c_hostname = _cffi_helper.cffi_cgopy_cnv_py2c_string(hostname)
    c_username = _cffi_helper.cffi_cgopy_cnv_py2c_string(username)
    c_password = _cffi_helper.cffi_cgopy_cnv_py2c_string(password)
    cret = _cffi_helper.lib.cgo_func_gossh_python_NewRPCSession(c_hostname, c_username, c_password, port, timeout)
    return cret


# pythonization of: gossh_python.RPCClose 
def RPCClose(sessionID):
    """RPCClose(long sessionID) object\n\nRPCClose closes\n"""
    cret = _cffi_helper.lib.cgo_func_gossh_python_RPCClose(sessionID)
    if not _cffi_helper.lib._cgopy_ErrorIsNil(cret):
        py_err_str = _cffi_helper.cffi_cgopy_cnv_c2py_errstring(cret)
        raise RuntimeError(py_err_str)
    return


# pythonization of: gossh_python.RPCConnect 
def RPCConnect(sessionID):
    """RPCConnect(long sessionID) object\n\nRPCConnect connects\n"""
    cret = _cffi_helper.lib.cgo_func_gossh_python_RPCConnect(sessionID)
    if not _cffi_helper.lib._cgopy_ErrorIsNil(cret):
        py_err_str = _cffi_helper.cffi_cgopy_cnv_c2py_errstring(cret)
        raise RuntimeError(py_err_str)
    return


# pythonization of: gossh_python.RPCGetShell 
def RPCGetShell(sessionID):
    """RPCGetShell(long sessionID) object\n\nRPCGetShell gets a shell\n"""
    cret = _cffi_helper.lib.cgo_func_gossh_python_RPCGetShell(sessionID)
    if not _cffi_helper.lib._cgopy_ErrorIsNil(cret):
        py_err_str = _cffi_helper.cffi_cgopy_cnv_c2py_errstring(cret)
        raise RuntimeError(py_err_str)
    return


# pythonization of: gossh_python.RPCRead 
def RPCRead(sessionID, size):
    """RPCRead(long sessionID, int size) str, object\n\nRPCRead reads data\n"""
    cret = _cffi_helper.lib.cgo_func_gossh_python_RPCRead(sessionID, size)
    if not _cffi_helper.lib._cgopy_ErrorIsNil(cret.r1):
        py_err_str = _cffi_helper.cffi_cgopy_cnv_c2py_errstring(cret.r1)
        raise RuntimeError(py_err_str)
    r0 = _cffi_helper.cffi_cgopy_cnv_c2py_string(cret.r0)
    return r0


# pythonization of: gossh_python.RPCWrite 
def RPCWrite(sessionID, data):
    """RPCWrite(long sessionID, str data) object\n\nRPCWrite reads data\n"""
    c_data = _cffi_helper.cffi_cgopy_cnv_py2c_string(data)
    cret = _cffi_helper.lib.cgo_func_gossh_python_RPCWrite(sessionID, c_data)
    if not _cffi_helper.lib._cgopy_ErrorIsNil(cret):
        py_err_str = _cffi_helper.cffi_cgopy_cnv_c2py_errstring(cret)
        raise RuntimeError(py_err_str)
    return


# pythonization of: gossh_python.SetPyPy 
def SetPyPy():
    """SetPyPy() \n\nSetPyPy is used by the Python side to declare whether or not we're running under PyPy (can't be discovered on the Go side)\n"""
    _cffi_helper.lib.cgo_func_gossh_python_SetPyPy()


# pythonization of: gossh_python.GetPyPy 
def GetPyPy():
    """GetPyPy() bool\n\nGetPyPy returns true if we're running under PyPy\n"""
    cret = _cffi_helper.lib.cgo_func_gossh_python_GetPyPy()
    ret = _cffi_helper.cffi_cgopy_cnv_c2py_bool(cret)
    return ret

