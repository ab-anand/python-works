'''Model for aircraft flights'''

class Flight:
	''' A flight with a particular passenger aircraft'''

	def __init__(self, number, aircraft):
		if not number[:2].isalpha():
			raise ValueError("No airline code in '{}'".format(number))

		if not number[:2].isupper():
			raise ValueError("Invalid airline code '{}'".format(number))

		if not (number[2:].isdigit() and int(number[2:]) <= 9999):
			raise ValueError("Invalid route number '{}'".format(number))

		self._number = number
		self._aircraft = aircraft

		rows, seats = self._aircraft.seating_plan()
		self._seating = [None] + [{letter: None for letter in seats} for _ in rows]

	def number(self):
		return self._number

	def airline(self):
		return self._number[:2]

	def aircraft_model(self):
		return self._aircraft.model()

	def _parse_seat(self, seat):
		"""Parse a seat designator into 
		a valid row and letter.

		Args:
			seat: A seat designator such as '12D'

		Returns: A tuple containing an integer for row and string for seat
		"""

		rows, seat_letters = self._aircraft.seating_plan()

		letter = seat[-1]
		if letter not in seat_letters:
			raise ValueError("Invalid seat letter '{}'".format(letter))

		row_text = seat[:-1]
		try:
			row = int(row_text)
		except ValueError:
			raise ValueError("Invalid seat row '{}'".format(row_text))

		if row not in rows:
			raise ValueError("Invalid row number '{}'".format(row))		

		return row, letter	

	def allocate_seat(self, seat, passenger):
		'''Allocate a seat to a passenger

		Args: 
			seat: A seat designator such as '12C'.
			passenger: The passenger name.

		Raises:
			ValueError: If the seat is not available
		'''
		
		row, letter = self._parse_seat(seat)

		if self._seating[row][letter] is not None:
			raise ValueError("Seat already occupied '{}'".format(seat))

		self._seating[row][letter] = passenger

	def relocate_passenger(self, from_seat, to_seat):
		"""Relocates a passenger from one seat to another.

		Args:
			from_seat: Current seat of the passenger
			to_seat: Seat the passenger wishes for 
		"""

		from_row, from_letter = self._parse_seat(from_seat)
		if self._seating[from_row][from_letter] is None:
			raise ValueError("No passenger to relocate from '{}'".format(from_seat))

		to_row, to_letter = self._parse_seat(to_seat)
		if self._seating[to_row][to_letter] is not None:
			raise ValueError("Seat '{}' already occupied".format(to_seat))

		self._seating[to_row][to_letter] = self._seating[from_row][from_letter]
		self._seating[from_row][from_letter] = None

	def num_seats_available(self):
		return sum(sum(1 for n in row.values() if n is None)
						for row in self._seating
						if row is not None)

	def make_boarding_cards(self, card_printer):
		for passenger, seat in sorted(self._passenger_seats()):
			card_printer(passenger, seat, self.number(), self.aircraft_model())

	def _passenger_seats(self):
		"""An iterable series of passenger seating allocations."""
		row_numbers, seat_letters = self._aircraft.seating_plan()
		for row in row_numbers:
			for letter in seat_letters:
				passenger = self._seating[row][letter]
				if passenger is not None:
					yield (passenger, "{}{}".format(row, letter))


class Aircraft:

	def __init__(self, registration):
		self._registration = registration

	def registration(self):
		return self._registration

	def num_seats(self):
		row, row_seats = self.seating_plan()
		return len(row)*len(row_seats)

class Boeing777(Aircraft):

	def model(self):
		return 'Boeing 777'

	def seating_plan(self):
		return range(1, 56), "ABCDEFGHJK"


class AirbusA319(Aircraft):

	def model(self):
		return 'Airbus A319'

	def seating_plan(self):
		return range(1, 23), "ABCDEF"


def make_flights():
	f = Flight('AB221', AirbusA319('G-BGT2'))
	f.allocate_seat('12A', 'Rahul')
	f.allocate_seat('15F', 'Dinesh Mathur')
	f.allocate_seat('15E', 'Christopher Philips')
	f.allocate_seat('1C', 'Tim Cathy')
	f.allocate_seat('1D', 'John Bushman') 

	g = Flight("AF72", Boeing777('F-GBPS'))
	g.allocate_seat('55K', 'Lisa Rosamund')
	g.allocate_seat('33G', "Hilary Burt")
	g.allocate_seat('4B', "Nikhil")
	g.allocate_seat('4A', 'Madhav')

	return f, g


def console_card_printer(passenger, seat, flight_number, aircraft):
	output = "| Name: {0}" \
			 "  Flight: {1}" \
			 "  Seat: {2}" \
			 "  Aircraft: {3}" \
			 " |".format(passenger, flight_number, seat, aircraft)

	banner = '+' + '-'*(len(output)-2) + '+'
	border = '|' + ' '*(len(output)-2) + '|'
	lines = [banner, border, output, border, banner]
	card = '\n'.join(lines)
	print(card)
	print()