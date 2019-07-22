from random import randint

answer=randint(20, 101)

guess=input("What umber you guess:")
guess_num=int(guess)

ma=100
mi=1

while guess_num!=answer:
	
	if guess_num > ma or guess_num < mi:
		print('Please try it again.')
		pass
	else:

		if guess_num > answer :
			ma=guess_num
			print("Answer range in %a and %b",mi,ma)
		else :
			mi=guess_num
			print("Answer range in %a and %b",mi,ma)

	guess=input("What umber you guess:")
	guess_num=int(guess)

print('Congrate!')		