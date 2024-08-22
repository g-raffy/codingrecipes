//==============================================================
//
// SAMPLE SOURCE CODE - SUBJECT TO THE TERMS OF SAMPLE CODE LICENSE AGREEMENT,
// http://software.intel.com/en-us/articles/intel-sample-source-code-license-agreement/
//
// Copyright 2016-2017 Intel Corporation
//
// THIS FILE IS PROVIDED "AS IS" WITH NO WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT
// NOT LIMITED TO ANY IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
// PURPOSE, NON-INFRINGEMENT OF INTELLECTUAL PROPERTY RIGHTS.
//
// =============================================================
/*******************************************************************************
*   This example measures performance of computing the real matrix product 
*   C=alpha*A*B+beta*C using Intel(R) MKL function dgemm, where A, B, and C are 
*   matrices and alpha and beta are double precision scalars. 
*
*   In this simple example, practices such as memory management, data alignment, 
*   and I/O that are necessary for good programming style and high MKL 
*   performance are omitted to improve readability.
********************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include "mkl.h"

int main(int argc, char*argv[])
{
    double *A, *B, *C;
    int m, n, p, i;
    double alpha, beta;
    double s_initial, s_elapsed;

    printf ("\n This example measures performance of Intel(R) MKL function dgemm \n"
            " computing real matrix C=alpha*A*B+beta*C, where A, B, and C \n"
            " are matrices and alpha and beta are double precision scalars\n\n");

    int size=atoi(argv[1]);
    double min_run_duration = (double)atof(argv[2]); // in seconds

    m = size, p = size, n = size;
    printf (" Initializing data for matrix multiplication C=A*B for matrix \n"
            " A(%ix%i) and matrix B(%ix%i)\n\n", m, p, p, n);
    alpha = 1.0; beta = 0.0;

    printf (" Allocating memory for matrices aligned on 64-byte boundary for better \n"
            " performance \n\n");
    A = (double *)mkl_malloc( m*p*sizeof( double ), 64 );
    B = (double *)mkl_malloc( p*n*sizeof( double ), 64 );
    C = (double *)mkl_malloc( m*n*sizeof( double ), 64 );
    if (A == NULL || B == NULL || C == NULL) {
        printf( "\n ERROR: Can't allocate memory for matrices. Aborting... \n\n");
        mkl_free(A);
        mkl_free(B);
        mkl_free(C);
        return 1;
    }

    printf (" Intializing matrix data \n\n");
    for (i = 0; i < (m*p); i++) {
        A[i] = (double)(i+1);
    }

    for (i = 0; i < (p*n); i++) {
        B[i] = (double)(-i-1);
    }

    for (i = 0; i < (m*n); i++) {
        C[i] = 0.0;
    }

    printf (" Making the first run of matrix product using Intel(R) MKL dgemm function \n"
            " via CBLAS interface to get stable run time measurements \n\n");
    cblas_dgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans, 
                m, n, p, alpha, A, p, B, n, beta, C, n);

    printf (" Measuring performance of matrix product using Intel(R) MKL dgemm function \n"
            " via CBLAS interface for at least %f seconds\n\n", min_run_duration);
    s_initial = dsecnd();
    int num_loops = 0;
    do
    {
        cblas_dgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans, 
                     m, n, p, alpha, A, p, B, n, beta, C, n);
        num_loops ++;
        s_elapsed = dsecnd() - s_initial;
    } while( s_elapsed < min_run_duration );
    double mean_mmul_duration = s_elapsed / num_loops;

    double num_ops=(double)m*p*n*2;
    double flops=num_ops/((double)mean_mmul_duration);
    printf (" == Matrix multiplication using Intel(R) MKL dgemm completed == \n"
            " == %d loops == \n"
            " == bench duration : %.5f seconds == \n"
            " == %f ops in %.5f seconds == \n"
            " == %.3f gflops == \n\n", num_loops, s_elapsed, num_ops, mean_mmul_duration, flops/1.e9);

    printf (" Deallocating memory \n\n");
    mkl_free(A);
    mkl_free(B);
    mkl_free(C);

    printf (" Dgemm2 Benchmark completed. \n\n");
    return 0;
}
