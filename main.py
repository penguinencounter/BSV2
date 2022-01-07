from svd import StudentVueContainer
from os import environ


sv = StudentVueContainer(environ['username'], environ['password'], environ['domain'])
sv.get_gradebook()
