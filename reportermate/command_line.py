import argparse
import codecs
from reportermate import analyseAndRender

parser = argparse.ArgumentParser()
parser.add_argument("data",help="The path to your data csv")
parser.add_argument("template",nargs='?', help="The path to your story template", default='')
parser.add_argument("options",nargs='?', help="A json file defining reportermate options",default='')
args = parser.parse_args()

def main():
	output = analyseAndRender(args.data, args.template, args.options)
	print(output)
	with codecs.open("story.txt", "w", encoding='utf8') as f:
		f.write(output)