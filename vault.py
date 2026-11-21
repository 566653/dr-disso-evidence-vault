"""Read-only local evidence manifest creator and verifier."""
import argparse,hashlib,json,pathlib,datetime
def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()
def create(files):
    return {"created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"algorithm":"SHA-256","evidence":[{"path":str(pathlib.Path(p).resolve()),"sha256":digest(p),"size":pathlib.Path(p).stat().st_size} for p in files]}
def verify(manifest):
    results=[]
    for item in manifest["evidence"]:
        p=pathlib.Path(item["path"])
        results.append({"path":str(p),"status":"OK" if p.is_file() and digest(p)==item["sha256"] else "MISMATCH_OR_MISSING"})
    return results
def main():
    ap=argparse.ArgumentParser()
    sp=ap.add_subparsers(dest="action",required=True)
    a=sp.add_parser("create");a.add_argument("files",nargs="+");a.add_argument("--output",default="manifest.json")
    b=sp.add_parser("verify");b.add_argument("manifest")
    args=ap.parse_args()
    if args.action=="create":
        m=create(args.files);pathlib.Path(args.output).write_text(json.dumps(m,indent=2),encoding="utf-8");print(args.output)
    else:
        r=verify(json.loads(pathlib.Path(args.manifest).read_text(encoding="utf-8")));print(json.dumps(r,indent=2));raise SystemExit(0 if all(x["status"]=="OK" for x in r) else 1)
if __name__=="__main__":main()
