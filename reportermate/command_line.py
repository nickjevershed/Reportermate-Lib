import argparse
from reportermate import analyseAndRender

parser = argparse.ArgumentParser()
parser.add_argument("data", help="The path to your data csv")
parser.add_argument("template", help="The path to your story template")
args = parser.parse_args()

def main():
	analyseAndRender(args.data, args.template)