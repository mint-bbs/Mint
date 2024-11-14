let userData = {};
adminRequest = false;

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

async function boardsMenu() {
  response = await fetch("/api/boards/", {
    method: "get",
  });

  if (response.status != 200) {
    document.cookie = "session=; max-age=-1;";
    window.location.reload();
    return;
  }

  let boards = await response.json();

  console.log(boards);
  let htmlData = "";
  boards.forEach((board) => {
    htmlData = `${htmlData}<button
              class="button is-fullwidth is-primary mt-3"
              onclick="boardEdit(${board.id});"
          >
              ${board.name} (ID: ${board.id})
          </button>\n`;
  });

  document.querySelector(".td").innerHTML = `
          <h1 class="title">板設定</h1>
          <p class="head">
              板の一覧を確認したり、板を作成したり、編集することができます。
          </p>
  
          <div class="boards">
            ${htmlData}
          </div>

            <hr>

          <button
              class="button is-fullwidth is-primary mt-3"
              onclick="mainmenu();"
          >
              メインメニュー
          </button>
  
          <button
              class="button is-fullwidth is-primary mt-3"
              onclick="metaDataMenu();"
          >
              メタデータ編集
          </button>
    `;
}

async function mainmenu() {
  response = await fetch("/api/admin/me", {
    method: "get",
    headers: {
      x_mint_session: getCookie("session"),
    },
  });

  if (response.status != 200) {
    document.cookie = "session=; max-age=-1;";
    window.location.reload();
    return;
  }

  userData = await response.json();

  document.querySelector(".td").innerHTML = `
        <h1 class="title">メインメニュー</h1>
        <p class="head">
            現在<b>${userData.username}</b>としてログイン中です。
        </p>

        <hr>

        <button
            class="button is-fullwidth is-primary mt-3"
            onclick="boardsMenu();"
        >
            板設定
        </button>

        <button
            class="button is-fullwidth is-primary mt-3"
            onclick="metaDataMenu();"
        >
            メタデータ編集
        </button>
  `;
}

async function request(e) {
  e.preventDefault();
  const submit = document.getElementById("submit");

  submit.disabled = true;
  submit.classList.add("is-loading");

  const formData = new FormData(e.target);

  if (formData.get("password") != formData.get("password_l")) {
    bulmaToast.toast({
      message: "パスワードが一致しません",
      type: "is-danger",
      duration: 5000,
      dismissible: false,
      pauseOnHover: true,
      position: "top-right",
      closeOnClick: false,
      extraClasses: "popup",
      animate: { in: "fadeIn", out: "fadeOut" },
    });
    submit.disabled = false;
    return;
  }

  body = {
    username: formData.get("username"),
    password: formData.get("password"),
    adminRequestPassWord: formData.get("adminRequestPassword"),
  };
  response = await fetch(`/api/admin/request`, {
    method: "post",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify(body),
  });
  try {
    jsonData = await response.json();
    console.log(jsonData);

    submit.classList.remove("is-loading");

    if (response.status == 200) {
      bulmaToast.toast({
        message: "リクエスト完了しました。",
        type: "is-success",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: false,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });

      await mainmenu();
    } else {
      bulmaToast.toast({
        message: "ログインに失敗しました。",
        type: "is-danger",
        duration: 5000,
        dismissible: true,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: true,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });
      setTimeout(function () {
        submit.disabled = false;
      }, 1000);
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
    setTimeout(function () {
      submit.disabled = false;
    }, 1000);
  }
}

async function login(e) {
  e.preventDefault();
  const submit = document.getElementById("submit");

  submit.disabled = true;
  submit.classList.add("is-loading");

  const formData = new FormData(e.target);
  body = {
    username: formData.get("username"),
    password: formData.get("password"),
  };
  response = await fetch(`/api/admin/login`, {
    method: "post",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify(body),
  });
  try {
    jsonData = await response.json();
    console.log(jsonData);

    submit.classList.remove("is-loading");

    if (response.status == 200) {
      bulmaToast.toast({
        message: "ログインしました。",
        type: "is-success",
        duration: 5000,
        dismissible: false,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: false,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });

      await mainmenu();
    } else {
      bulmaToast.toast({
        message: "ログインに失敗しました。",
        type: "is-danger",
        duration: 5000,
        dismissible: true,
        pauseOnHover: true,
        position: "top-right",
        closeOnClick: true,
        extraClasses: "popup",
        animate: { in: "fadeIn", out: "fadeOut" },
      });
      setTimeout(function () {
        submit.disabled = false;
      }, 1000);
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
    setTimeout(function () {
      submit.disabled = false;
    }, 1000);
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  response = await fetch("/api/admin/data");
  jsonData = await response.json();

  if (!getCookie("session")) {
    if (jsonData.userCount == 0) {
      adminRequest = true;

      document.querySelector(".title").textContent =
        "管理者アカウントリクエスト";
      document.querySelector(".head").innerHTML =
        "Mintを利用するには、管理者アカウントをリクエストする必要があります。使用したいユーザー名、パスワード、そして<b>管理者リクエストパスワード</b>を入力してください。";
      document.querySelector(".formInput").innerHTML = `${
        document.querySelector(".formInput").innerHTML
      }\n
                    パスワード(確認)：<input
                    type="password"
                    name="password_l"
                    size="19"
                    class="input"
                    required
                    />
        \n管理者リクエストパスワード：<input
                    type="password"
                    name="adminRequestPassword"
                    size="19"
                    class="input"
                    required
                    />`;
      document.getElementById("submit").textContent = "リクエスト";
      document.getElementById("postForm").onsubmit = request;
    } else {
      document.getElementById("postForm").onsubmit = login;
    }
  } else {
    await mainmenu();
  }
});
