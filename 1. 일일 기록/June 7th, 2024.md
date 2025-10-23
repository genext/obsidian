---
title: "June 7th, 2024"
created: 2024-06-07 09:22:50
updated: 2024-06-07 17:26:37
---
  * 16:20 codestral을 설치
    * pip install mistral_inference
      * 에러 ModuleNotFoundError: No module named 'torch'
        * ```javascript
PS C:\exercise\codestral> pip install mistral_inference  
Collecting mistral_inference
  Using cached mistral_inference-1.1.0-py3-none-any.whl.metadata (8.9 kB)
Collecting fire>=0.6.0 (from mistral_inference)
  Using cached fire-0.6.0.tar.gz (88 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Installing backend dependencies ... done
  Preparing metadata (pyproject.toml) ... done
Collecting mistral_common<2.0.0,>=1.0.0 (from mistral_inference)
  Using cached mistral_common-1.2.1-py3-none-any.whl.metadata (3.6 kB)
Collecting safetensors>=0.4.0 (from mistral_inference)
  Using cached safetensors-0.4.3-cp312-none-win_amd64.whl.metadata (3.9 kB)
Collecting simple-parsing>=0.1.5 (from mistral_inference)
  Using cached simple_parsing-0.1.5-py3-none-any.whl.metadata (7.7 kB)
Collecting xformers>=0.0.24 (from mistral_inference)
  Using cached xformers-0.0.26.post1.tar.gz (4.1 MB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... error
  error: subprocess-exited-with-error

  × Getting requirements to build wheel did not run successfully.
  │ exit code: 1
  ╰─> [20 lines of output]
      Traceback (most recent call last):
        File "C:\Python312\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 353, in <module>
          main()
        File "C:\Python312\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 335, in main
          json_out['return_val'] = hook(**hook_input['kwargs'])
                                   ==^====^====^====^====^==^^^
        File "C:\Python312\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 118, in get_requires_for_build_wheel
          return hook(config_settings)
        File "C:\Users\jkoh5\AppData\Local\Temp\pip-build-env-a0byyv6i\overlay\Lib\site-packages\setuptools\build_meta.py", line 325, in get_requires_for_build_wheel          return self._get_build_requires(config_settings, requirements=['wheel'])
                 ==^====^====^====^====^====^====^====^====^====^====^====^====^==
        File "C:\Users\jkoh5\AppData\Local\Temp\pip-build-env-a0byyv6i\overlay\Lib\site-packages\setuptools\build_meta.py", line 295, in _get_build_requires
          self.run_setup()
        File "C:\Users\jkoh5\AppData\Local\Temp\pip-build-env-a0byyv6i\overlay\Lib\site-packages\setuptools\build_meta.py", line 487, in run_setup
          super().run_setup(setup_script=setup_script)
        File "C:\Users\jkoh5\AppData\Local\Temp\pip-build-env-a0byyv6i\overlay\Lib\site-packages\setuptools\build_meta.py", line 311, in run_setup
          exec(code, locals())
        File "<string>", line 23, in <module>
      ModuleNotFoundError: No module named 'torch'
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
error: subprocess-exited-with-error

× Getting requirements to build wheel did not run successfully.
│ exit code: 1
╰─> See above for output.

note: This error originates from a subprocess, and is likely not a problem with pip.```
      * python list를 실행하면 torch가 설치된 것을 확인할 수 있지만 더 자세한 테스트 프로그램 돌리면 CUDA 사용할 수 없다고 나옴.
        * ```javascript
import torch

# Check if PyTorch is installed
print("PyTorch version:", torch.*version*)

# Check if CUDA is available (optional, for GPU support)
if torch.cuda.is_available():
    print("CUDA is available. You can use GPU.")
else:
    print("CUDA is not available. You can only use CPU."```
      * CUDA 설치 여부 확인하기 위해 nvcc --version을 실행하면 nvcc 못 찾음.
      * [NVDIA web](https://developer.nvidia.com/cuda-downloads)에서 cuda sdk 다운로드 & 설치
        * cpu compatibility 확인해야 한다고 했지만 일단 건너뜀
      * torchvision, torchaudio 설치
        * pip으로 설치할 때 에러가 나면 --user 옵션을 추가. 
      * torch, torchvision, torchaudio와 cuda 버전 연결 설치까지 하고 나서 다시 처음 실패한 pip install mistral_inference 설치 시도
        * ```javascript
 pip install torch==2.3.1+cu118 torchvision==0.18.1+cu118 torchaudio==2.3.1+cu118 -f https://download.pytorch.org/whl/cu118/torch_stable.html --user```