class Rectangle:
   def __init__(self, length, breadth, unit_cost=0):
       self.length = length
       self.breadth = breadth
       self.unit_cost = unit_cost
       self.perimeter=2 * (length + breadth)
       self.Area=length * breadth
       self.cost=self.Area * unit_cost


#   def get_perimeter(self):
 #      return 2 * (self.length + self.breadth)
   
   def get_area(self):
       return self.Area
   
  # def calculate_cost(self):
   #    area = self.get_area()
    #   return area * self.unit_cost
# breadth = 120 cm, length = 160 cm, 1 cm^2 = Rs 2000
r = Rectangle(160, 120, 2000)
print("Area of Rectangle: %s cm^2" %(r.Area))
#print("Cost of rectangular field: Rs. %s " %(r.calculate_cost()))