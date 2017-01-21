class A():
	def __init__(self, B):
		self.B = B

	def call_B_method(self):
		self.B.activate_method()


class B():
	def __init__(self):
		pass

	def activate_method(self):
		print "ACTIVATING THE METHOD !"




print "start...."

object_B = B()
object_A = A(object_B)
object_A.call_B_method()


print "that's the show folks ~"