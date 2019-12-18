POPCLIP = URLtoAlfred
POPCLIP_EXT = $(POPCLIP).popclipext
POPCLIP_EXTZ = $(POPCLIP).popclipextz

popclip:
	cp -r $(POPCLIP) $(POPCLIP_EXT)
	zip -r $(POPCLIP_EXTZ) $(POPCLIP_EXT)
	rm -r $(POPCLIP_EXT)