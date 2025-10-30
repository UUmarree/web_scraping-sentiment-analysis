import sys

def error_message_Details(error, error_detail:sys):
    error_detail.exc_info()
    _,_,exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    error_message = "Error occurred in script: [{0}] at line number: [{1}] error message: [{2}]".format(
        file_name
    ) 