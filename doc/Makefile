
# vim: noexpandtab

RSTS  = $(wildcard *.rst)
HTMLS = $(RSTS:.rst=.html)

all: $(HTMLS)

%.html: %.rst
	rstweave --full -o $@ $<

clean:
	rm -f $(HTMLS)

