
func_dict = { # this is a set of function that needs to be transferred
       '__libc_exit_fini' :'libc_exit_fini',
        'fdopen': '__fdopen',
        '___errno_location': '__errno_location',
        'ofl_lock': '__ofl_lock',
        '__isoc99_sscanf': 'sscanf',
        # '__lctrans_impl': '__lctrans', this was so wrong, they were two different funcs, happened when looking at chown
        '_IO_getc': 'getc',
        '_IO_putc': 'putc',
        'lstat64': 'lstat',
        'stat64': 'stat',
        'open64': 'open',
        'lseek64': 'lseek',
        'readdir64': 'readdir',
        'fstat64': 'fstat',
        'pthread_mutex_lock': '__pthread_mutex_lock',
        'pthread_mutex_unlock': '__pthread_mutex_unlock',
        'pthread_create': '__pthread_create',
        'pthread_once': '__pthread_once',
        'pthread_cond_timedwait': '__pthread_cond_timedwait',
        'pthread_key_create': '__pthread_key_create',
        'pthread_getspecific': '__pthread_getspecific',
        'pthread_rwlock_trywrlock': '__pthread_rwlock_trywrlock', 
        'pthread_join':'__pthread_join',
        'clock_gettime': '__clock_gettime',
        'crc32': 'crc32z',
        'adler32': 'adler32z',
        }

unnec = { # this is a set of functions that does not need to be transferred
        '__funcs_on_exit': 1,
        'mal': 1,
        'net': 1, 
        '__abort_lock': 1,
        '_fini': 1,
        'all_mask': 1,
        'main.bonus': 1,
        'progNameReally': 1,
        'outName': 1,
        'inName': 1,
        'tmpName': 1,
        'fileMetaInfo': 1,
        '__stderr_FILE': 1,
        '__stdout_FILE': 1,
        '__stdin_FILE': 1,
        }

syscall_patterns = [ # this is a set of syscall patterns
        r'%\d+\s=\stail\scall\si64\s@__syscall_cp\(i64\s(\d+),',
        r'%\d+\s=\stail\scall\sfastcc\si64\s@__syscall_cp\(i64\s(\d+),',
        r"%\d+\s=\scall\si64\s@__syscall_cp\(i64\s(\d+),",
        r"%\d+\s=\scall\sfastcc\si64\s@__syscall_cp\(i64\s(\d+),",
        r'syscall,\s=\\\{ax\\\},\\\{ax\\\},[^\(]*\}\s?[\s\(]\s?i64\s(\d+)',
        r'syscall,\s=\\\{ax\\\},\\\{ax\\\},\\\{di\\\},\\\{si\\\},~\\\{rcx\\\},~\\\{r11\\\},~\\\{memory\\\},~\\\{dirflag\\\},~\\\{fpsr\\\},~\\\{flags\\\}\(i64\s(\d+)'
        ]


