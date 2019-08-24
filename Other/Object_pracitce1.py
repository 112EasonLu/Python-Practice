class Human:
	def __init__(self,h,w):
		self.height = h
		self.weight = w
	def BMI(self):
		return self.weight / ((self.height/100)**2)


a =Human(180,80)
print("BMI is %s" % a.BMI())