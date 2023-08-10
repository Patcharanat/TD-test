import sys
import os
import configparser

# input cli: python3 text_sanitizer.py input.txt output.txt True
# input cli: python3 text_sanitizer.py

class TextSanitizer:
    """
    Read text from source file (or source database), sanitize it, and write to target file.
    """
    def __init__(self, source: str, target: str = None, write_out: bool = False):
        try:
            # classify input
            if source.endswith(".txt"):
                # read text from source file
                with open(source, "r") as f:
                    text = f.read()
                f.close()
            elif 'mongodb.net' in source: # source = "mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@cluster.mongodb.net/"
                # read text from source database
                # the process of sanitization might be different from reading from file e.g. using pymongo and pandas to handle data
                pass
        except:
            raise ValueError('Error from "source" argument')

        # assign to class variables
        self.text = text
        self.target = target
        self.write_out = write_out

    def sanitize_input(self, text: str) -> str:
        """
        Sanitize input text
        """
        # lowercase input
        output = text.lower()

        # replace tab characters
        output = output.replace("\t", "____") # tab
        output = output.replace("     ", "____") # 5 spaces
        output = output.replace("   ", "____") # 3 spaces
        output = output.replace("  ", "____") # 2 spaces
        
        return output
    
    def count_alphabet(self, text: str) -> int:
        """
        count alphabet in input text
        """
        output = text.strip()
        output = output.replace(" ", "")
        return len(output)
    
    def any_other_sanitization(self, text: str) -> str:
        """
        you can add more sanitization here as class functions or methods
        """
        return text
    
    def write_output(self, text: str) -> None:
        """
        write output to target file if 'write_out' is True
        """
        with open(self.target, "w") as f:
            f.write(text)
        f.close()
        return

    def main(self) -> None:
        """
        main function to run the class
        """
        sanitized_text = self.sanitize_input(self.text)
        count_alpha = self.count_alphabet(self.text)
        sanitized_text = self.any_other_sanitization(sanitized_text)

        if self.write_out == True:
            self.write_output(sanitized_text)

        print(f"Sanitized Text:{sanitized_text} \nCount Alphabet:{count_alpha}")
        return
    
if __name__ == "__main__":
    # get source and target arguments from cli
    try:
        source = sys.argv[1]
        target = sys.argv[2]
        write_out = sys.argv[3]
        if write_out == "True":
            write_out = True
        else:
            write_out = False
    except:
        source = None
        target = None
        write_out = None
    # if source and target are not specified, automatically read from config file, or ask user to input
    if source:
        pass
    elif os.path.exists("configFile"):
        # read config file
        config = configparser.ConfigParser()
        # config["section"]["key"]
        source = config["DEFAULT"]["Source"]
        target = config["DEFAULT"]["Target"]
        write_out = config["DEFAULT"]["WriteOut"]
    else:
        print("Type in source file: ")
        source = input()
        print("Type in target file: ")
        target = input()
        print("Want to write out as a file? (y/n)")
        write_out = input()
        if write_out == "y":
            write_out = True
        else:
            write_out = False

    # if source is not specified, raise error
    if source == "":
        raise ValueError("Source file is not specified")
    
    TextSanitizer(source, target, write_out).main()