import time
import httpx
from api.settings import API_TOKEN

# this assumes API server is running at :5000 and that worker is also running

DELAY = 1  # seconds


def poll_until_done(job_id, current=0, max=100):
    r = httpx.get(
        f"http://localhost:5000/api/reports/status/{job_id}?token={API_TOKEN}"
    )
    json = r.json()
    status = json["status"]
    progress = json.get("progress")

    if status == "success":
        print(f"Results at: {json['result']}")
        return

    if status == "failed":
        print(f"Failed: {json['detail']}")
        return

    print(f"Progress: {progress}")

    current += 1
    if current == max:
        print("Max retries hit, stopping...")
        return

    time.sleep(DELAY)

    poll_until_done(job_id, current=current, max=max)


def test_upload_file():
    files = {"file": open("examples/api/Razor.zip", "rb")}
    r = httpx.post(
        f"http://localhost:5000/api/reports/custom?token={API_TOKEN}",
        data={"name": "foo"},
        files=files,
    )
    job_id = r.json()["job"]

    poll_until_done(job_id)


def test_huc12_report(huc12_id):
    r = httpx.post(
        f"http://localhost:5000/api/reports/huc12/{huc12_id}?token={API_TOKEN}"
    )
    job_id = r.json()["job"]

    poll_until_done(job_id)


if __name__ == "__main__":
    # test_upload_file()
    test_huc12_report("0")

    # test_huc12_report("030602040601")

