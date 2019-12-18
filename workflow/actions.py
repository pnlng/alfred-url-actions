import sys
from workflow import Workflow

def main(wf):
    # Loop through the returned posts and add an item for each to
    # the list of results for Alfred
    wf.add_item(title="what",
                subtitle="is")

    # Send the results to Alfred as XML
    wf.send_feedback()

if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))