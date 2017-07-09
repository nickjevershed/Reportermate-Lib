import reportermate
from pybars import Compiler

context = {
	"dogs":1,
	"cats":2,
	"birds":3,
	"list":[5,3,6,7]
}

def modifyObject(con, arg):
	return sorted(context['list'])

templateString = u"This is a test of {{modifyObject 'blah'}} and {{dogs}}"

compiler = Compiler()
template = compiler.compile(templateString)

helpers = {"modifyObject":modifyObject}

output = template(context,helpers=helpers)

print output