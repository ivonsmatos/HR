"""
GPU Support Configuração for Helix Assistant

Enables CUDA/ROCm acceleration for Ollama models:
- Automatic GPU detection
- CUDA/ROCm initialization
- Fallback to CPU if GPU unavailable
- Performance monitoring

Installation:
    # CUDA (NVIDIA)
    export CUDA_VISIBLE_DEVICES=0
    export OLLAMA_NUM_GPU=1

    # ROCm (AMD)
    export HSA_OVERRIDE_GFX_VERSION=gfx906
    export OLLAMA_NUM_GPU=-1  # All GPUs
"""

import os
import logging
import subprocess
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class GPUType(Enum):
    """GPU Types Supported"""
    NVIDIA_CUDA = "cuda"
    AMD_ROCM = "rocm"
    CPU = "cpu"


class GPUManager:
    """Manage GPU acceleration for Ollama"""
    
    @staticmethod
    def detect_gpu() -> Dict[str, any]:
        """
        Detect available GPU hardware
        
        Returns:
        {
            'gpu_type': 'cuda' | 'rocm' | 'cpu',
            'device_count': int,
            'device_memory': [GB, GB, ...],
            'driver_version': str,
            'available': bool,
        }
        """
        try:
            # Check NVIDIA CUDA
            if GPUManager._check_nvidia():
                return {
                    'gpu_type': 'cuda',
                    'device_count': GPUManager._get_cuda_device_count(),
                    'device_memory': GPUManager._get_cuda_memory(),
                    'driver_version': GPUManager._get_cuda_version(),
                    'available': True,
                }
            
            # Check AMD ROCm
            elif GPUManager._check_rocm():
                return {
                    'gpu_type': 'rocm',
                    'device_count': GPUManager._get_rocm_device_count(),
                    'device_memory': GPUManager._get_rocm_memory(),
                    'driver_version': GPUManager._get_rocm_version(),
                    'available': True,
                }
            
            # Fallback to CPU
            else:
                return {
                    'gpu_type': 'cpu',
                    'device_count': 0,
                    'device_memory': [],
                    'driver_version': None,
                    'available': False,
                }
        
        except Exception as e:
            logger.warning(f"GPU detection failed: {e}")
            return {
                'gpu_type': 'cpu',
                'device_count': 0,
                'device_memory': [],
                'driver_version': None,
                'available': False,
                'error': str(e)
            }
    
    @staticmethod
    def _check_nvidia() -> bool:
        """Check if NVIDIA CUDA is available"""
        try:
            subprocess.run(
                ['nvidia-smi', '--query-gpu=count', '--format=csv,noheader'],
                capture_output=True,
                timeout=5,
                check=True
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    def _check_rocm() -> bool:
        """Check if AMD ROCm is available"""
        try:
            subprocess.run(
                ['rocm-smi', '--showproductname'],
                capture_output=True,
                timeout=5,
                check=True
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    def _get_cuda_device_count() -> int:
        """Get number of CUDA devices"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=count', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return int(result.stdout.strip().split('\n')[0])
        except Exception:
            return 0
    
    @staticmethod
    def _get_cuda_memory() -> List[int]:
        """Get CUDA device memory in GB"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.total', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Convert MB to GB
            return [int(int(m) / 1024) for m in result.stdout.strip().split('\n')]
        except Exception:
            return []
    
    @staticmethod
    def _get_cuda_version() -> Optional[str]:
        """Get CUDA version"""
        try:
            result = subprocess.run(
                ['nvidia-smi'],
                capture_output=True,
                text=True,
                timeout=5
            )
            for line in result.stdout.split('\n'):
                if 'CUDA Versão' in line:
                    return line.split('CUDA Versão')[1].strip().split('|')[0].strip()
        except Exception:
            pass
        return None
    
    @staticmethod
    def _get_rocm_device_count() -> int:
        """Get number of ROCm devices"""
        try:
            result = subprocess.run(
                ['rocm-smi', '--showproductname'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return len([l for l in result.stdout.split('\n') if 'GPU' in l and 'gfx' in l])
        except Exception:
            return 0
    
    @staticmethod
    def _get_rocm_memory() -> List[int]:
        """Get ROCm device memory in GB"""
        try:
            result = subprocess.run(
                ['rocm-smi', '--showmeminfo', 'vram'],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Parse output
            memory_list = []
            for line in result.stdout.split('\n'):
                if 'VRAM Total' in line:
                    # Extract memory value in MB
                    parts = line.split()
                    if parts:
                        try:
                            memory_mb = int(parts[-2])
                            memory_list.append(memory_mb // 1024)
                        except ValueErro:
                            pass
            return memory_list
        except Exception:
            return []
    
    @staticmethod
    def _get_rocm_version() -> Optional[str]:
        """Get ROCm version"""
        try:
            result = subprocess.run(
                ['rocm-smi', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except Exception:
            pass
        return None
    
    @staticmethod
    def configure_environment(gpu_type: str = 'auto') -> Dict[str, str]:
        """
        Configure environment variables for GPU acceleration
        
        Args:
            gpu_type: 'cuda', 'rocm', 'cpu', or 'auto' (detect)
        
        Returns:
            Dict of environment variables to set
        """
        env_vars = {}
        
        if gpu_type == 'auto':
            detection = GPUManager.detect_gpu()
            gpu_type = detection['gpu_type']
        
        if gpu_type == 'cuda':
            # NVIDIA CUDA Configuração
            env_vars = {
                'CUDA_VISIBLE_DEVICES': os.getenv('CUDA_VISIBLE_DEVICES', '0'),
                'OLLAMA_NUM_GPU': os.getenv('OLLAMA_NUM_GPU', '1'),
                'CUDA_HOME': '/usr/local/cuda',
                'LD_LIBRARY_PATH': '/usr/local/cuda/lib64:${LD_LIBRARY_PATH}',
            }
        
        elif gpu_type == 'rocm':
            # AMD ROCm Configuração
            env_vars = {
                'ROCM_HOME': '/opt/rocm',
                'LD_LIBRARY_PATH': '/opt/rocm/lib:${LD_LIBRARY_PATH}',
                'HSA_OVERRIDE_GFX_VERSION': os.getenv('HSA_OVERRIDE_GFX_VERSION', ''),
                'OLLAMA_NUM_GPU': os.getenv('OLLAMA_NUM_GPU', '-1'),
            }
        
        else:
            # CPU Only
            env_vars = {
                'OLLAMA_NUM_GPU': '0',
            }
        
        return env_vars
    
    @staticmethod
    def get_performance_metrics() -> Dict[str, any]:
        """Get GPU performance metrics"""
        detection = GPUManager.detect_gpu()
        
        if not detection['available']:
            return {
                'gpu_available': False,
                'mode': 'CPU',
                'speedup': '1x',
                'estimated_memory': '~16GB',
                'estimated_response_time': '5-15s',
            }
        
        gpu_type = detection['gpu_type']
        device_count = detection['device_count']
        device_memory = detection['device_memory']
        
        if gpu_type == 'cuda':
            speedup = '2-3x' if device_count >= 1 else '1x'
            total_vram = sum(device_memory) if device_memory else 0
            estimated_memory = f"~{total_vram - 4}GB" if total_vram > 4 else '~GPU memory'
            response_time = '1-3s' if device_count >= 1 else '5-15s'
        
        elif gpu_type == 'rocm':
            speedup = '1.5-2.5x' if device_count >= 1 else '1x'
            total_vram = sum(device_memory) if device_memory else 0
            estimated_memory = f"~{total_vram - 4}GB" if total_vram > 4 else '~GPU memory'
            response_time = '2-5s' if device_count >= 1 else '5-15s'
        
        else:
            speedup = '1x'
            estimated_memory = '~16GB'
            response_time = '5-15s'
        
        return {
            'gpu_available': True,
            'mode': gpu_type.upper(),
            'device_count': device_count,
            'device_memory_gb': device_memory,
            'speedup': speedup,
            'estimated_memory': estimated_memory,
            'estimated_response_time': response_time,
            'driver_version': detection['driver_version'],
        }
