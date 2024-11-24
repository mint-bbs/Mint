const cachedResponses = [];
let socketConnected = false;

let board = location.pathname.split("/")[3];
let key = location.pathname.split("/")[4];

const AudioContext =
  window.AudioContext ||
  window.webkitAudioContext ||
  window.mozAudioContext ||
  window.oAudioContext ||
  window.msAudioContext;
const audioContext = new AudioContext();

let source = audioContext.createBufferSource();
let audioBuffer;

fetch("/static/sounds/notification.mp3")
  .then((response) => response.arrayBuffer())
  .then((arrayBuffer) => audioContext.decodeAudioData(arrayBuffer))
  .then((buffer) => {
    audioBuffer = buffer;
  })
  .catch((error) => console.error(error));

function playSound() {
  if (!audioBuffer) return;

  const source = audioContext.createBufferSource();
  source.buffer = audioBuffer;
  source.connect(audioContext.destination);
  source.start();
}

function connectSocketIO(threadId) {
  const socket = io();

  socket.on("connect", () => {
    bulmaToast.toast({
      message: "通知サーバーに接続しました。",
      type: "is-success",
      duration: 500,
      dismissible: false,
      pauseOnHover: true,
      position: "top-right",
      closeOnClick: false,
      extraClasses: "popup",
      animate: { in: "fadeIn", out: "fadeOut" },
    });

    socket.emit("join_room", `thread_${threadId}`);
  });

  socket.on("global_count_event", (data) => {
    document.getElementById("globalViews").textContent = `${data.count}人`;
    document.getElementById("globalMaxViews").textContent = `/ ${data.max}人`;
  });

  socket.on("count_event", (data) => {
    document.getElementById("localViews").textContent = `${data.count}人`;
    document.getElementById("localMaxViews").textContent = `/ ${data.max}人`;
  });

  socket.on("thread_writed", (data) => {
    bulmaToast.toast({
      message: "レス + 1",
      type: "is-success",
      duration: 2000,
      dismissible: false,
      pauseOnHover: true,
      position: "top-right",
      closeOnClick: false,
      extraClasses: "popup",
      animate: { in: "fadeIn", out: "fadeOut" },
    });
    playSound();

    cachedResponses.push(JSON.parse(data));
    console.log(cachedResponses);
    console.log(cachedResponses.length);
    refreshThread(cachedResponses);
  });
}

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

function formatDate(date) {
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  const seconds = String(date.getSeconds()).padStart(2, "0");
  const milliseconds = String(date.getMilliseconds()).padStart(3, "0");
  const week = ["日", "月", "火", "水", "木", "金", "土"];
  const w = week[date.getDay()];

  return `${yyyy}/${mm}/${dd}(${w}) ${hours}:${minutes}:${seconds}.${milliseconds}`;
}

async function refreshThread(responses, threadId) {
  const progressBar = document.getElementById("progress");

  const responsesElement = document.querySelector(".responses");

  let count = 0;
  const nodes = [];

  let ownerId;

  var returnDate = new Date();

  document.querySelector(".progress-bar").innerHTML =
    '<progress id="progress" class="progress is-link" value="0" max="2">Now Loading...</progress>';

  responses.forEach((response) => {
    count += 1;

    const node = document.createElement("div");
    node.classList.add("thread");
    node.id = `response_${count}`;

    const date = new Date(response.created_at);
    if (count == 1) {
      document.querySelector(".thread-title").textContent = response.title;
      returnDate = date;
      ownerId = response.account_id;
    }

    let ownerFlag = "";

    if (response.account_id == ownerId) {
      ownerFlag = '<span class="owner">主</span>';
    } else {
      ownerFlag = "";
    }

    node.innerHTML = `<span onclick="document.querySelector('.textarea').textContent += '>>${count}'">${count}：</span><span style="color: green;"><b>${
      response.name
    }</b></span>：${formatDate(date)} ID: ${response.account_id}${ownerFlag}`;

    const content = document.createElement("div");
    content.classList.add("content");
    response.content = response.content.replaceAll(
      /((?<!href="|href='|src="|src=')(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gi,
      "<a href='$1'>$1</a>"
    );
    response.content = response.content.replaceAll(
      /&gt;&gt;(\d{1,4}(-\d{1,4})?(,\d{1,4}(-\d{1,4})?)*)/g,
      (match, group) => {
        const targets = group
          .split(",")
          .map((part) => {
            if (part.includes("-")) {
              const [start, end] = part.split("-").map(Number);
              return Array.from(
                { length: end - start + 1 },
                (_, i) => start + i
              );
            }
            return [Number(part)];
          })
          .flat();

        return `<span class="response-link" data-targets="${targets.join(
          ","
        )}">&gt;&gt;${group}</span>`;
      }
    );

    response.content = response.content.replaceAll("\n", " <br> ");

    content.innerHTML = response.content.replaceAll(
      /&gt;&gt;(\d{1,4}(?:-\d{1,4})?(?:,\d{1,4}(?:-\d{1,4})?)*)/g,
      "<a href='#response_$1'><span class='response-link' data-targets='$1'>&gt;&gt;$1</span></a>"
    );

    node.append(content);

    nodes.push(node);

    progressBar.value = count;
  });

  responsesElement.innerHTML = "";
  nodes.forEach((node) => responsesElement.appendChild(node));
  progressBar.remove();

  if (!socketConnected) {
    connectSocketIO(threadId);
    socketConnected = true;
  }

  return returnDate;
}

async function post(e) {
  e.preventDefault();
  const submit = document.getElementById("submit");

  submit.disabled = true;
  submit.classList.add("is-loading");

  const formData = new FormData(e.target);
  body = {
    name: formData.get("name"),
    authKey: formData.get("authKey"),
    content: formData.get("content"),
  };
  response = await fetch(`/api/boards/${board}/threads/${key}`, {
    method: "put",
    headers: {
      "content-type": "application/json",
      Cookie: `2ch_X=${getCookie("2ch_X")}`,
    },
    body: JSON.stringify(body),
  });
  try {
    jsonData = await response.json();
    console.log(jsonData);

    submit.classList.remove("is-loading");

    if (response.status == 200) {
      bulmaToast.toast({
        message: "スレッドに書き込みました。",
        type: "is-success",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: false,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });
      e.target.querySelector("textarea[name=content]").value = "";
      submit.disabled = false;
    } else {
      bulmaToast.toast({
        message: jsonData.detail,
        type: "is-danger",
        duration: 5000,
        dismissible: true,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: true,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });
      submit.disabled = false;
      submit.classList.remove("is-loading");
    }
  } catch {
    bulmaToast.toast({
      message: "不明なエラーが発生しました。",
      type: "is-danger",
      duration: 5000,
      dismissible: true,
      pauseOnHover: true,
      position: "top-right",
      closeOnClick: true,
      extraClasses: "popup",
      animate: { in: "fadeIn", out: "fadeOut" },
    });
    submit.disabled = false;
    submit.classList.remove("is-loading");
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  const progressBar = document.getElementById("progress");

  const name = getCookie("NAME");
  if (name == null) {
    document.getElementById("name").value = "";
  } else {
    document.getElementById("name").value = getCookie("NAME");
  }

  const response = await fetch(`/api/boards/${board}/threads/${key}`);
  const data = await response.text();
  const responses = JSON.parse(data);
  console.log(responses);
  const threadId = responses[0].id;
  progressBar.max = responses.length;
  responses.forEach((response) => {
    cachedResponses.push(response);
  });
  date = await refreshThread(responses, threadId);

  document.querySelector(".size").textContent = `${data.length}KB`;

  let nowDate = new Date();
  nowTime = (nowDate.getTime() - date.getTime()) / 1000 / 60;
  ikioi = (responses.length / nowTime) * 60 * 24;
  document.getElementById("ikioi").textContent = `勢い: ${ikioi}`;

  const postForm = document.getElementById("postForm");
  postForm.addEventListener("submit", post);

  setupTooltip();
});

function setupTooltip() {
  const tooltip = document.createElement("div");
  tooltip.classList.add("tooltip");
  tooltip.style.position = "absolute";
  tooltip.style.pointerEvents = "none";
  tooltip.style.backgroundColor = "#ABABABCC";
  tooltip.style.backdropFilter = "blur(1px)";
  tooltip.style.zIndex = 10000;
  tooltip.style.color = "black";
  tooltip.style.padding = "5px 10px";
  tooltip.style.borderRadius = "5px";
  tooltip.style.fontSize = "12px";
  tooltip.style.display = "none";
  document.body.appendChild(tooltip);

  document.body.addEventListener("mouseover", (e) => {
    if (e.target.classList.contains("response-link")) {
      const targets = e.target.getAttribute("data-targets").split(",");

      // 解析されたターゲットの範囲またはIDを取得
      const targetResponses = targets
        .map((part) => {
          if (part.includes("-")) {
            // 範囲形式（例: 1-5）に対応
            let [start, end] = part.split("-").map(Number);
            if (end > 1000) {
              end = 1000;
            }
            return Array.from({ length: end - start + 1 }, (_, i) => start + i);
          } else {
            // 個別IDに対応
            return [Number(part)];
          }
        })
        .flat()
        .map((id) => {
          const responseElement = document.getElementById(`response_${id}`);
          return responseElement
            ? responseElement.innerHTML
            : `<div>レス ${id} は存在しません</div>`;
        });

      // 取得したレスをツールチップに表示
      tooltip.innerHTML = targetResponses.join("<hr>"); // 各レスを区切る
      tooltip.style.display = "block";
    }
  });

  document.body.addEventListener("mousemove", (e) => {
    tooltip.style.left = `${e.pageX + 20}px`; // カーソルの少し右側に表示
    tooltip.style.top = `${e.pageY + 20}px`; // カーソルの少し下側に表示
  });

  document.body.addEventListener("mouseout", (e) => {
    if (e.target.classList.contains("response-link")) {
      tooltip.style.display = "none";
    }
  });
}
