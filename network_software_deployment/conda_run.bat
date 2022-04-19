@ECHO ON
:: call "C:\Users\<username>\anaconda3\Scripts\activate.bat
call ""  
:: call activate <conda enviroment with tf installed>
call activate tf-gpu
python software_nn_test.py
pause
