import reportermate

print(reportermate.analyseAndRender('expenses.csv', 'expenses-template.txt', 'expenses-replace.json'))
print(reportermate.analyseAndRender('unemployment.csv', 'unemployment-template.txt'))
print(reportermate.analyseAndRender('donations.csv', 'donations-template.txt', 'donations-replace.json'))
