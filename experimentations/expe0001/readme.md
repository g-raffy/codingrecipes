this experimentation aims at finding if an application using intel mkl (with threads) needs to have libiomp5 in its LD_LIBRARY_PATH. This work is related to []

# journal

## 22/08/2024

```sh
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ module list
Currently Loaded Modulefiles:
 1) lib/mkl/latest  
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ module show lib/mkl/latest
-------------------------------------------------------------------
/usr/share/modules/modulefiles/lib/mkl/latest:

module-whatis   {Sets the Environment to use the Intel Math Kernel Libraries version 2024.2.1}
setenv          MKLROOT /opt/intel/oneapi-2024.2.1/mkl/2024.2
prepend-path    PKG_CONFIG_PATH /opt/intel/oneapi-2024.2.1/mkl/2024.2/lib/pkgconfig
prepend-path    CMAKE_PREFIX_PATH /opt/intel/oneapi-2024.2.1/mkl/2024.2/lib/cmake
prepend-path    PATH /opt/intel/oneapi-2024.2.1/mkl/2024.2/bin/
prepend-path    NLSPATH /opt/intel/oneapi-2024.2.1/mkl/2024.2/share/locale/%l_%t/%N
prepend-path    LD_LIBRARY_PATH /opt/intel/oneapi-2024.2.1/mkl/2024.2/lib
prepend-path    CPATH /opt/intel/oneapi-2024.2.1/mkl/2024.2/include
prepend-path    LIBRARY_PATH /opt/intel/oneapi-2024.2.1/mkl/2024.2/lib/
-------------------------------------------------------------------
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ pkgconfig mkl
-bash: pkgconfig: command not found
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ pkg
pkgconf     pkg-config  pkgdata     
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ pkg-config mkl
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ pkg-config 
Please specify at least one package name on the command line.
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ pkg-config mkl
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ ls /opt/intel/oneapi-2024.2.1/mkl/2024.2/lib/pkgconfig
mkl-dynamic-ilp64-gomp.pc  mkl-dynamic-ilp64-tbb.pc  mkl-dynamic-lp64-seq.pc  mkl-static-ilp64-gomp.pc	mkl-static-ilp64-tbb.pc  mkl-static-lp64-seq.pc
mkl-dynamic-ilp64-iomp.pc  mkl-dynamic-lp64-gomp.pc  mkl-dynamic-lp64-tbb.pc  mkl-static-ilp64-iomp.pc	mkl-static-lp64-gomp.pc  mkl-static-lp64-tbb.pc
mkl-dynamic-ilp64-seq.pc   mkl-dynamic-lp64-iomp.pc  mkl-sdl.pc		      mkl-static-ilp64-seq.pc	mkl-static-lp64-iomp.pc
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ pkg-config mkl-dynamic-lp64-iomp
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ pkg-config mkl-dynamic-lp64-iomp --libs
Package openmp was not found in the pkg-config search path.
Perhaps you should add the directory containing `openmp.pc'
to the PKG_CONFIG_PATH environment variable
Package 'openmp', required by 'mkl-dynamic-lp64-iomp', not found
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ man pkg-config
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ pkgconf mkl-dynamic-lp64-iomp --libs
Package openmp was not found in the pkg-config search path.
Perhaps you should add the directory containing `openmp.pc'
to the PKG_CONFIG_PATH environment variable
Package 'openmp', required by 'mkl-dynamic-lp64-iomp', not found
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ pkgconf --cflags mkl-dynamic-lp64-iomp
Package openmp was not found in the pkg-config search path.
Perhaps you should add the directory containing `openmp.pc'
to the PKG_CONFIG_PATH environment variable
Package 'openmp', required by 'mkl-dynamic-lp64-iomp', not found
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ module avail
------------------------------------------------------------------------------------- /usr/share/modules/modulefiles --------------------------------------------------------------------------------------
compilers/ifort/15.0.2     lib/cuda/11.8.89              lib/mkl/2018.0.1           lib/mpi/intelmpi/2019.0.3   programming/julia/1.10.0       science/hibricol/1.0.5   science/molpro/2015.1.44  
compilers/ifort/17.0.1     lib/cuda/latest               lib/mkl/2019.0.3           lib/mpi/intelmpi/2019.0.7   programming/julia/latest       science/hibricol/latest  science/molpro/latest     
compilers/ifort/18.0.1     lib/maths/magma/2.7.0         lib/mkl/2020.0.1           lib/mpi/intelmpi/2021.13.0  science/comsol/5.6             science/lammps/2023.8.2  use.own                   
compilers/ifort/19.0.3     lib/maths/magma/latest        lib/mkl/2024.2.1           lib/mpi/intelmpi/latest     science/comsol/latest          science/lammps/latest    
compilers/ifort/19.1.1     lib/maths/suitesparse/5.10.1  lib/mkl/latest             module-git                  science/gaussian/16.1.3        science/ls-dyna/11.1.0   
compilers/ifort/2021.13.1  lib/maths/suitesparse/latest  lib/mpi/intelmpi/5.0.1     module-info                 science/gaussian/ifort/16.1.3  science/ls-dyna/latest   
compilers/ifort/latest     lib/mkl/11.2.2                lib/mpi/intelmpi/2017.0.1  modules                     science/gaussian/ifort/latest  science/matlab/9.14.0    
dot                        lib/mkl/2017.0.1              lib/mpi/intelmpi/2018.0.1  null                        science/gaussian/latest        science/matlab/latest    

Key:
loaded  modulepath  
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ module load compilers/ifort/2021.13.1
Loading compilers/ifort/2021.13.1
  Loading requirement: lib/mkl/2024.2.1
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ module avail
------------------------------------------------------------------------------------- /usr/share/modules/modulefiles --------------------------------------------------------------------------------------
compilers/ifort/15.0.2     lib/cuda/11.8.89              lib/mkl/2018.0.1           lib/mpi/intelmpi/2019.0.3   programming/julia/1.10.0       science/hibricol/1.0.5   science/molpro/2015.1.44  
compilers/ifort/17.0.1     lib/cuda/latest               lib/mkl/2019.0.3           lib/mpi/intelmpi/2019.0.7   programming/julia/latest       science/hibricol/latest  science/molpro/latest     
compilers/ifort/18.0.1     lib/maths/magma/2.7.0         lib/mkl/2020.0.1           lib/mpi/intelmpi/2021.13.0  science/comsol/5.6             science/lammps/2023.8.2  use.own                   
compilers/ifort/19.0.3     lib/maths/magma/latest        lib/mkl/2024.2.1           lib/mpi/intelmpi/latest     science/comsol/latest          science/lammps/latest    
compilers/ifort/19.1.1     lib/maths/suitesparse/5.10.1  lib/mkl/latest             module-git                  science/gaussian/16.1.3        science/ls-dyna/11.1.0   
compilers/ifort/2021.13.1  lib/maths/suitesparse/latest  lib/mpi/intelmpi/5.0.1     module-info                 science/gaussian/ifort/16.1.3  science/ls-dyna/latest   
compilers/ifort/latest     lib/mkl/11.2.2                lib/mpi/intelmpi/2017.0.1  modules                     science/gaussian/ifort/latest  science/matlab/9.14.0    
dot                        lib/mkl/2017.0.1              lib/mpi/intelmpi/2018.0.1  null                        science/gaussian/latest        science/matlab/latest    

Key:
loaded  modulepath  auto-loaded  
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ pkgconf --cflags mkl-dynamic-lp64-iomp
-I/opt/intel/oneapi-2024.2.1/mkl/2024.2/lib/pkgconfig/../../include -I/opt/intel/oneapi-2024.2.1/compiler/2024.2/lib/pkgconfig/../../include 
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ pkgconf --libs mkl-dynamic-lp64-iomp
-L/opt/intel/oneapi-2024.2.1/mkl/2024.2/lib/pkgconfig/../../lib -lmkl_intel_lp64 -lmkl_intel_thread -lmkl_core -lpthread -lm -ldl -L/opt/intel/oneapi-2024.2.1/compiler/2024.2/lib/pkgconfig/../../lib/ -liomp5 
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ pkgconf --libs mkl-dynamic-lp64-gomp
-m64 -L/opt/intel/oneapi-2024.2.1/mkl/2024.2/lib/pkgconfig/../../lib -Wl,--no-as-needed -lmkl_intel_lp64 -lmkl_gnu_thread -lmkl_core -lgomp -lpthread -lm -ldl 
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ module unload compilers/ifort/2021.13.1
Unloading compilers/ifort/2021.13.1
  Unloading useless requirement: lib/mkl/2024.2.1
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ pkgconf --libs mkl-dynamic-lp64-iomp
Package openmp was not found in the pkg-config search path.
Perhaps you should add the directory containing `openmp.pc'
to the PKG_CONFIG_PATH environment variable
Package 'openmp', required by 'mkl-dynamic-lp64-iomp', not found
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ pkgconf --libs mkl-dynamic-lp64-gomp
-m64 -L/opt/intel/oneapi-2024.2.1/mkl/2024.2/lib/pkgconfig/../../lib -Wl,--no-as-needed -lmkl_intel_lp64 -lmkl_gnu_thread -lmkl_core -lgomp -lpthread -lm -ldl 
graffy@alambix97:/opt/ipr/cluster/work.local/graffy/codingrecipes/experimentations/expe0001$ pkgconf --cflags mkl-dynamic-lp64-gomp
-m64 -I/opt/intel/oneapi-2024.2.1/mkl/2024.2/lib/pkgconfig/../../include 
```


```sh
20240822-18:43:11 graffy@graffy-ws2:~/private/dev/codingrecipes.git/experimentations/expe0001$ ./expe0001.py &> expe001.stdout
last command status : [0]
```

conclusion:
1. [text](expe001.stdout) shows that mkl's dgemm can run succesfully without libiomp5
2. libiomp5 is only required if the user wants mkl-dynamic-lp64-iomp (intel openmp) instead of mkl-dynamic-lp64-gomp (gnu openmp)
