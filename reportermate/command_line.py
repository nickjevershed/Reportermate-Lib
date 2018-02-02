import argparse
import codecs
from reportermate import analyseAndRender

parser = argparse.ArgumentParser()
parser.add_argument("data",help="The path to your data csv")
parser.add_argument("template",nargs='?', help="The path to your story template", default='')
parser.add_argument("replacements",nargs='?', help="A json file with key-value pairs for the strings and the replacement strings",default='')
args = parser.parse_args()

def main():
	output = analyseAndRender(args.data, args.template, args.replacements)
	print(output)
	with codecs.open("story.txt", "w", encoding='utf8') as f:
		f.write(output)