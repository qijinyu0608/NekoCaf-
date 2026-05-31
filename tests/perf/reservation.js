import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  scenarios: {
    reservation_read: {
      executor: "ramping-vus",
      stages: [
        { duration: "30s", target: 20 },
        { duration: "1m", target: 50 },
        { duration: "30s", target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_duration: ["p(95)<350"],
    http_req_failed: ["rate<0.01"],
  },
};

export default function () {
  const response = http.get(
    "http://127.0.0.1:8000/api/slots?storeId=store-shanghai-jingan&date=2026-05-20&partySize=2",
  );
  check(response, { "slots returned": (r) => r.status === 200 });
  sleep(1);
}
