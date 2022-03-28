package main

import (
	"encoding/json"
	"fmt"
	"github.com/deanishe/awgo"
	"io/ioutil"
	"net/url"
	"os"
	"os/exec"
	"regexp"
	"strings"
)

const CustomActionsVar = "CUSTOM_ACTIONS"
const CustomActionsFileVar = "CUSTOM_ACTIONS_FILE"
const CleanAmazonVar = "CLEAN_AMAZON"

var wf *aw.Workflow

func init() {
	wf = aw.New()
}

type Action struct {
	ActionTitle    string `json:"action_title"`
	ActionSubtitle string `json:"action_subtitle"`
	Output         string `json:"output"`
	Encode         bool   `json:"encode"`
}

var defaultActions = []Action{
	{
		ActionTitle: "Copy as Markdown link",
		Output:      "[{title}]({url})",
	},
	{
		ActionTitle: "Copy as Markdown list item",
		Output:      "- [{title}]({url})",
	},
	{
		ActionTitle:    "Add to OmniFocus",
		ActionSubtitle: "",
		Output:         "omnifocus:///add?name={title}&note={url}",
		Encode:         true,
	},
	{
		ActionTitle: "Copy Title",
		Output:      "{title}",
	},
	{
		ActionTitle: "Copy URL",
		Output:      "{url}",
	},
	{
		ActionTitle: "Copy HTML link",
		Output:      "<a href=\"{url}\">{title}</a>",
	},
}

func runAppleScript(script string) string {
	out, err := exec.Command("osascript", "-l", "JavaScript", "-e", script).Output()
	if err != nil {
		wf.FatalError(err)
	}
	return strings.TrimSpace(string(out[:]))
}

func getAppId() string {
	return runAppleScript("Application('System Events').applicationProcesses.where({frontmost:true}).bundleIdentifier()[0]")
}

func getTitle(appId string) string {
	return runAppleScript(fmt.Sprintf("Application('%s').windows[0].name()", appId))
}

func cleanAmazonUrl(url string) string {
	return regexp.MustCompile(`(^.*/(?:dp|gp/product)/([^/?]+)).*$`).ReplaceAllString(url, `$1`)
}

func run() {
	var inputUrl string
	args := wf.Args()
	switch len(args) {
	case 0:
		inputUrl = ""
	default:
		inputUrl = args[0]
	}
	if strings.ToLower(os.Getenv(CleanAmazonVar)) == "true" {
		inputUrl = cleanAmazonUrl(inputUrl)
	}
	var actions []Action
	var jsonErr error
	if customActionsFile := os.Getenv(CustomActionsFileVar); customActionsFile != "" {
		customActionsFilePath := fmt.Sprintf("%s/%s", wf.DataDir(), customActionsFile)
		content, readErr := ioutil.ReadFile(customActionsFilePath)
		if len(content) == 0 {
			wf.Fatalf("No actions in %s!", customActionsFile)
		}
		if readErr != nil {
			wf.Fatalf("Error reading %s!", customActionsFile)
		}
		jsonErr = json.Unmarshal(content, &actions)
		if jsonErr != nil {
			wf.Fatalf("%s is malformed!", customActionsFile)
		}
	} else if customActions := os.Getenv(CustomActionsVar); customActions != "" {
		jsonErr = json.Unmarshal([]byte(customActions), &actions)
		if jsonErr != nil {
			wf.Fatalf("%s is malformed!", CustomActionsVar)
		}
	} else {
		actions = defaultActions
	}
	appId := getAppId()
	title := getTitle(appId)
	for _, action := range actions {
		var formattedTitle string
		if action.Encode {
			formattedTitle = url.PathEscape(title)
		} else {
			formattedTitle = title
		}
		replacer := strings.NewReplacer("{title}", formattedTitle, "{url}", inputUrl)
		formattedOutput := replacer.Replace(action.Output)
		// Use the formatted string as subtitle if it's not specified in the json
		subtitle := action.ActionSubtitle
		if subtitle == "" {
			subtitle = formattedOutput
		}
		wf.NewItem(action.ActionTitle).Subtitle(subtitle).Arg(formattedOutput).Valid(true)
	}
	wf.SendFeedback()
}

func main() {
	wf.Run(run)
}
