.DEFAULT_GOAL = copy

FILE_NAME = main

POPCLIP = URLtoAlfred
POPCLIP_EXT = $(POPCLIP).popclipext
POPCLIP_EXTZ = $(POPCLIP).popclipextz

.PHONY: popclip
popclip:
	cp -r $(POPCLIP) $(POPCLIP_EXT)
	zip -r $(POPCLIP_EXTZ) $(POPCLIP_EXT)
	rm -r $(POPCLIP_EXT)

.PHONY: build
build:
	env GOOS=darwin GOARCH=amd64 go build "$(FILE_NAME).go"

.PHONY: copy
copy: build
	cp $(FILE_NAME) ${WORKFLOW_PATH}
	chmod a+x "${WORKFLOW_PATH}/$(FILE_NAME)"
