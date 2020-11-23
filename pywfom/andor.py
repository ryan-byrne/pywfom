from ctypes import POINTER, c_int, c_uint, c_double
import time, os, ctypes, platform, queue, cv2, threading, sys
import numpy as np

_stdcall_libraries = {}

arch, plat = platform.architecture()

if platform.mac_ver()[0] != "":
    msg = "AndorSDK3 is not currently compatible with MacOS"
    raise OSError(msg)

if plat.startswith('Windows'):
    try:
        _stdcall_libraries['ATCORE'] = ctypes.WinDLL('atcore.dll')
        _stdcall_libraries['ATUTIL'] = ctypes.WinDLL('atutility.dll')
    except:
        msg = 'atcore and atutlity DLL not found'
        raise OSError(msg)
else:
    try:
        _stdcall_libraries['ATCORE'] = ctypes.CDLL('atcore.so')
        _stdcall_libraries['ATUTIL'] = ctypes.CDLL('atutility.so')
    except:
        msg = 'atcore and atutlity DLL not found'
        raise OSError(msg)

class AndorError(Exception):
    def __init__(self, func, num):

        if num == 100:
            num = 0
        error_list = [
            'AT_ERR_HARDWARE_OVERFLOW',
            'AT_ERR_NOTINITIALISED',
            'AT_ERR_NOTIMPLEMENTED',
            'AT_ERR_READONLY',
            'AT_ERR_NOTREADABLE',
            'AT_ERR_NOTWRITABLE',
            'AT_ERR_OUTOFRANGE',
            'AT_ERR_INDEXNOTAVAILABLE',
            'AT_ERR_INDEXNOTIMPLEMENTED',
            'AT_ERR_EXCEEDEDMAXSTRINGLENGTH',
            'AT_ERR_CONNECTION',
            'AT_ERR_NODATA',
            'AT_ERR_INVALIDHANDLE',
            'AT_ERR_TIMEDOUT',
            'AT_ERR_BUFFERFULL',
            'AT_ERR_INVALIDSIZE',
            'AT_ERR_INVALIDALIGNMENT',
            'AT_ERR_COMM',
            'AT_ERR_STRINGNOTAVAILABLE',
            'AT_ERR_STRINGNOTIMPLEMENTED',
            'AT_ERR_NULL_FEATURE',
            'AT_ERR_NULL_HANDLE',
            'AT_ERR_NULL_IMPLEMENTED_VAR',
            'AT_ERR_NULL_READABLE_VAR',
            'AT_ERR_NULL_READONLY_VAR',
            'AT_ERR_NULL_WRITABLE_VAR',
            'AT_ERR_NULL_MINVALUE',
            'AT_ERR_NULL_MAXVALUE',
            'AT_ERR_NULL_VALUE',
            'AT_ERR_NULL_STRING',
            'AT_ERR_NULL_COUNT_VAR',
            'AT_ERR_NULL_ISAVAILABLE_VAR',
            'AT_ERR_NULL_MAXSTRINGLENGTH',
            'AT_ERR_NULL_EVCALLBACK',
            'AT_ERR_NULL_QUEUE_PTR',
            'AT_ERR_NULL_WAIT_PTR',
            'AT_ERR_NULL_PTRSIZE',
            'AT_ERR_NOMEMORY',
        ]
        self.error = error_list[num]
        self.func = func
    def __str__(self):
        return "{0} while running {1}".format(self.error[:7], self.func)

# typedefs
AT_H = ctypes.c_int
AT_BOOL = ctypes.c_int
AT_64 = ctypes.c_int64
AT_U8 = ctypes.c_uint8
AT_16 = ctypes.c_int16
AT_U16 = ctypes.c_uint16
AT_WC = ctypes.c_wchar

AT_INFINITE = 0xFFFFFFFF
AT_CALLBACK_SUCCESS = 0

AT_TRUE = 1
AT_FALSE = 0

AT_SUCCESS = 0

# special case for buffer timeout
AT_ERR_TIMEDOUT = 13
AT_ERR_NODATA = 11


class TimeoutError(AndorError):
    pass

AT_HANDLE_UNINITIALISED = -1
AT_HANDLE_SYSTEM = 1

### Functions ###
STRING = POINTER(AT_WC)

# classes so that we do some magic and automatically add byrefs etc ... can classify outputs

class _meta(object):
    pass

class OUTPUT(_meta):
    def __init__(self, val):
        self.type = val
        self.val = POINTER(val)

    def getVar(self, bufLen=0):
        v = self.type()
        return v, ctypes.byref(v)

class _OUTSTRING(OUTPUT):
    def __init__(self):
        self.val = STRING

    def getVar(self, bufLen):
        v = ctypes.create_unicode_buffer(bufLen)
        return v, v

OUTSTRING = _OUTSTRING()

class _OUTSTRLEN(_meta):
    def __init__(self):
        self.val = c_int

OUTSTRLEN = _OUTSTRLEN()

def stripMeta(val):
    if isinstance(val, _meta):
        return val.val
    else:
        return val

class dllFunction(object):
    def __init__(self, name, args=[], argnames=[], lib='ATCORE'):
        self.f = getattr(_stdcall_libraries[lib], name)
        self.f.restype = c_int
        self.f.argtypes = [stripMeta(a) for a in args]

        self.fargs = args
        self.fargnames = argnames
        self.name = name

        self.inp = [not isinstance(a, OUTPUT) for a in args]
        self.in_args = [a for a in args if not isinstance(a, OUTPUT)]
        self.out_args = [a for a in args if isinstance(a, OUTPUT)]

        self.buf_size_arg_pos = -1
        for i in range(len(self.in_args)):
            if isinstance(self.in_args[i], _OUTSTRLEN):
                self.buf_size_arg_pos = i

        ds = name + '\n\nArguments:\n===========\n'
        for i in range(len(args)):
            an = ''
            if i < len(argnames):
                an = argnames[i]
            ds += '\t%s\t%s\n' % (args[i], an)

        self.f.__doc__ = ds

    def __call__(self, *args):
        ars = []
        i = 0
        ret = []

        if self.buf_size_arg_pos >= 0:
            bs = args[self.buf_size_arg_pos]
        else:
            bs = 255

        for j in range(len(self.inp)):
            if self.inp[j]:  # an input
                ars.append(args[i])
                i += 1
            else:  # an output
                r, ar = self.fargs[j].getVar(bs)
                ars.append(ar)
                ret.append(r)
                # print r, r._type_

        # print ars
        res = self.f(*ars)
        # print res

        if not res == AT_SUCCESS:
            if res == AT_ERR_TIMEDOUT or res == AT_ERR_NODATA:
                # handle timeouts as a special case, as we expect to get them
                raise TimeoutError(self.name, res)
            else:
                raise AndorError(self.name, res)

        if len(ret) == 0:
            return None
        if len(ret) == 1:
            return ret[0]
        else:
            return ret

def dllFunc(name, args=[], argnames=[], lib='ATCORE'):
    f = dllFunction(name, args, argnames, lib)
    globals()[name[3:]] = f

dllFunc('AT_InitialiseLibrary')
dllFunc('AT_FinaliseLibrary')

dllFunc('AT_Open', [c_int, OUTPUT(AT_H)])
dllFunc('AT_Close', [AT_H])

dllFunc('AT_IsImplemented', [AT_H, STRING, OUTPUT(AT_BOOL)])
dllFunc('AT_IsReadable', [AT_H, STRING, OUTPUT(AT_BOOL)])
dllFunc('AT_IsWritable', [AT_H, STRING, OUTPUT(AT_BOOL)])
dllFunc('AT_IsReadOnly', [AT_H, STRING, OUTPUT(AT_BOOL)])

dllFunc('AT_SetInt', [AT_H, STRING, AT_64])
dllFunc('AT_GetInt', [AT_H, STRING, OUTPUT(AT_64)])
dllFunc('AT_GetIntMax', [AT_H, STRING, OUTPUT(AT_64)])
dllFunc('AT_GetIntMin', [AT_H, STRING, OUTPUT(AT_64)])

dllFunc('AT_SetFloat', [AT_H, STRING, c_double])
dllFunc('AT_GetFloat', [AT_H, STRING, OUTPUT(c_double)])
dllFunc('AT_GetFloatMax', [AT_H, STRING, OUTPUT(c_double)])
dllFunc('AT_GetFloatMin', [AT_H, STRING, OUTPUT(c_double)])

dllFunc('AT_SetBool', [AT_H, STRING, AT_BOOL])
dllFunc('AT_GetBool', [AT_H, STRING, OUTPUT(AT_BOOL)])

dllFunc('AT_SetEnumerated', [AT_H, STRING, c_int])
dllFunc('AT_SetEnumeratedString', [AT_H, STRING, STRING])
dllFunc('AT_GetEnumerated', [AT_H, STRING, OUTPUT(c_int)])
dllFunc('AT_GetEnumeratedCount', [AT_H, STRING, OUTPUT(c_int)])
dllFunc('AT_IsEnumeratedIndexAvailable', [AT_H, STRING, c_int, OUTPUT(AT_BOOL)])
dllFunc('AT_IsEnumeratedIndexImplemented', [AT_H, STRING, c_int, OUTPUT(AT_BOOL)])
dllFunc('AT_GetEnumeratedString', [AT_H, STRING, c_int, OUTSTRING, OUTSTRLEN])

dllFunc('AT_SetEnumIndex', [AT_H, STRING, c_int])
dllFunc('AT_SetEnumString', [AT_H, STRING, STRING])
dllFunc('AT_GetEnumIndex', [AT_H, STRING, OUTPUT(c_int)])
dllFunc('AT_GetEnumCount', [AT_H, STRING, OUTPUT(c_int)])
dllFunc('AT_IsEnumIndexAvailable', [AT_H, STRING, c_int, OUTPUT(AT_BOOL)])
dllFunc('AT_IsEnumIndexImplemented', [AT_H, STRING, c_int, OUTPUT(AT_BOOL)])
dllFunc('AT_GetEnumStringByIndex', [AT_H, STRING, c_int, OUTSTRING, OUTSTRLEN])

dllFunc('AT_Command', [AT_H, POINTER(AT_WC)])

dllFunc('AT_SetString', [AT_H, STRING, STRING])
dllFunc('AT_GetString', [AT_H, STRING, OUTSTRING, OUTSTRLEN])
dllFunc('AT_GetStringMaxLength', [AT_H, STRING, OUTPUT(c_int)])

dllFunc('AT_QueueBuffer', [AT_H, POINTER(AT_U8), c_int])
dllFunc('AT_WaitBuffer', [AT_H, OUTPUT(POINTER(AT_U8)), OUTPUT(c_int), c_uint])
dllFunc('AT_Flush', [AT_H])

#####################################
# Utility library (for unpacking etc ...)
dllFunc('AT_InitialiseUtilityLibrary', lib='ATUTIL')
dllFunc('AT_FinaliseUtilityLibrary', lib='ATUTIL')
dllFunc('AT_ConvertBuffer', [POINTER(AT_U8), POINTER(AT_U8), AT_64, AT_64, AT_64, STRING, STRING], lib='ATUTIL')
dllFunc('AT_ConvertBufferUsingMetadata', [POINTER(AT_U8), POINTER(AT_U8), AT_64, STRING], lib='ATUTIL')

InitialiseUtilityLibrary()
InitialiseLibrary()
