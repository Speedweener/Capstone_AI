#include "top.h"

void dense_relu_1(const io_pt (&input)[NUMBER_OF_INPUTS], fixed_pt &output, const ap_int<8> index)
{
	fixed_pt product;
	fixed_pt result = bias_1[index];
	for (int i = 0; i < NUMBER_OF_INPUTS; i++)
	{
		#pragma HLS pipeline
		#pragma HLS UNROLL factor=2
		product = input[i] * weights_1[i][index];
		result += product;
	}

	if (result > 0)
		output = result;
	else
		output = 0;


}

void dense_relu_2(const fixed_pt (&input)[NUMBER_OF_NODES], fixed_pt &output, const ap_int<8> index)
{

	fixed_pt product;
	fixed_pt result = bias_2[index];
	for (int i = 0; i < NUMBER_OF_NODES; i++)
	{
		#pragma HLS pipeline
		#pragma HLS UNROLL factor=2
		product = input[i] * weights_2[i][index];
		result += product;
	}


	if (result > 0)
		output = result;
	else
		output = 0;

}


void max_in_array(fixed_pt (&input)[NUMBER_OF_OUTPUTS], io_pt (&output)[NUMBER_OF_OUTPUTS])
{
	fixed_pt max_value = 0;
	ap_uint<3> index = 0;

	for (int i = 0; i < NUMBER_OF_OUTPUTS; i++)
	{
		#pragma HLS pipeline
		if(input[i] > max_value) {
			index = i;
			max_value = input[i];
		}
	}
	for (int i = 0; i < NUMBER_OF_OUTPUTS; i++)
	{
		if(i == index)
			output[i] = 1;
		else
			output[i] = 0;
	}
}



void output_layer(const fixed_pt (&input)[NUMBER_OF_NODES], fixed_pt &output, const ap_int<8> index)
{

	fixed_pt product;
	fixed_pt result = bias_3[index];
	for (int i = 0; i < NUMBER_OF_NODES; i++)
	{
		#pragma HLS pipeline
		#pragma HLS UNROLL factor=2

		product = input[i] * weights_3[i][index];
		result += product;
	}

	output = result;

}




void main_fun(stream_io& S_AXIS, stream_io& M_AXIS)
{
	#pragma HLS INTERFACE ap_ctrl_none port=return
	#pragma HLS INTERFACE axis port=S_AXIS
	#pragma HLS INTERFACE axis port=M_AXIS



	io_pt input[NUMBER_OF_INPUTS];
	fixed_pt output[NUMBER_OF_NODES];
	fixed_pt output_2[NUMBER_OF_NODES];
	fixed_pt output_3[NUMBER_OF_OUTPUTS];
	io_pt final_output[NUMBER_OF_OUTPUTS] = {0};

	#pragma HLS array_partition variable=output
	#pragma HLS array_partition variable=output_2

	#pragma HLS array_partition variable=output_3

	AXI_IO in;
	AXI_IO out;

	loadinputs:for (int i = 0; i < NUMBER_OF_INPUTS; i++) {
			#pragma HLS pipeline
			#pragma HLS UNROLL factor=2

			S_AXIS >> in;
			input[i] = in.data;
	}


	multiply_1:for (int i = 0; i < NUMBER_OF_NODES; i++) {   // Dense Layer 1 with relu
			dense_relu_1(input, output[i], i);
	}

	multiply_2:for (int i = 0; i < NUMBER_OF_NODES; i++) {   // Dense Layer 2 with relu
			dense_relu_2(output, output_2[i], i);
	}

	multiply_3:for (int i = 0; i < NUMBER_OF_OUTPUTS; i++) { // Output Layer 3
			output_layer(output_2, output_3[i], i);
	}

	max_in_array(output_3, final_output); // Output max function


	send:for (int i = 0; i < NUMBER_OF_OUTPUTS; i++) {
			out.data = final_output[i];
			if (i == NUMBER_OF_OUTPUTS - 1)
				out.last = in.last;
			else
				out.last = 0;
			M_AXIS.write(out);
	}

}

