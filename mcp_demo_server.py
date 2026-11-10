from __future__ import annotations
import json, sys

ISSUES = {
    "101": {"id":"101","title":"Fix edit uniqueness check","status":"open","body":"Ensure edit refuses 0 or multiple matches."},
    "102": {"id":"102","title":"Add tool trace panel","status":"closed","body":"Show tool name, args, result and errors in UI."},
}

TOOLS=[{
    "name":"get_issue",
    "description":"查询课程演示 issue。用户要求查 issue 或任务单时使用。",
    "inputSchema":{"type":"object","properties":{"issue_id":{"type":"string","description":"issue id，如 101"}},"required":["issue_id"]}
}]

def respond(rid, result=None, error=None):
    msg={"jsonrpc":"2.0","id":rid}
    if error is not None:
        msg["error"]={"code":-32000,"message":str(error)}
    else:
        msg["result"]=result
    sys.stdout.write(json.dumps(msg, ensure_ascii=False)+"\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        req={}
        try:
            req=json.loads(line)
            rid=req.get("id")
            if req.get("method")=="tools/list":
                respond(rid,{"tools":TOOLS})
            elif req.get("method")=="tools/call":
                params=req.get("params",{})
                if params.get("name")!="get_issue":
                    raise ValueError("unknown tool")
                issue_id=str(params.get("arguments",{}).get("issue_id",""))
                issue=ISSUES.get(issue_id)
                if not issue:
                    raise ValueError(f"issue not found: {issue_id}")
                respond(rid,{"content":[{"type":"text","text":json.dumps(issue,ensure_ascii=False)}]})
            else:
                raise ValueError("unknown method")
        except Exception as exc:
            respond(req.get("id"), error=exc)

if __name__=="__main__":
    main()
