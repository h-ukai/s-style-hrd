/*
 * 東日本REINS 新システム
 * Copyright (C) 2008. REAL ESTATE INFORMATION NETWORK FOR EAST JAPAN.
 *
 * <b>変更履歴：</b>2010/05/16 Satoshi Koyanagi SY_0365 図面・CSVボタン２度押し防止<br>
 *
 */

var submitFlg = false;

/**
 * 先頭のフォームに対してsubmitを行う。
 */
function submitFirst() {

    if (submitFlg) {
        return;
    }

    submitFlg = true;
    // フォームオブジェクト
    var frm = document.forms[0];

    if (frm == null) {
		return false;
    }

    frm.submit();
}

function submitFirstD(b) {

    if (submitFlg) {
        return;
    }

    submitFlg = true;
    // フォームオブジェクト
    var frm = document.forms[0];

    if (frm == null) {
		return false;
    }

    frm.submit();
    b.disabled = true;
}


/**
 * 任意のフォームに対してsubmitを行う。
 *
 * @param frmId フォームオブジェクトのID属性値
 */
function submitForm(frmId) {

    if (submitFlg) {
        return;
    }

    submitFlg = true;
    // フォームオブジェクト
    var frm = document.getElementsByName(frmId);

    if (frm.length != 1) {
        return false;
    }

    frm[0].submit();
}

/**
 * 任意のフォームに対してsubmitを行う。
 *
 * @param idx フォームの要素番号
 */
function submitFormElement(idx) {

    if (submitFlg) {
        return;
    }

    submitFlg = true;
    // フォームオブジェクト
    var frm = document.forms[idx];

    if (frm.length == null) {
        return false;
    }

    frm.submit();
}

/**
 * ボタン押下時に制御オブジェクトの表示／非表示を行う。
 *
 * 注意事項
 * 　クロスブラウザ対応として制御オブジェクトは<div>または<span>を使用すること。
 * 　制御オブジェクトに<table>を使用するとMozilla系ブラウザでレイアウトが崩れて
 * 　しまう。
 *
 * @param btnId ボタンオブジェクトのID属性値
 * @param ctrlId 制御オブジェクトのID属性値
 * @param dispBtnValue 表示時のボタン名
 * @param nonDispBtnValue 非表示時のボタン名
 */
function switchLayer(btnId, ctrlId, dispBtnValue, nonDispBtnValue) {

    // ボタンオブジェクト
    var btnObj = document.getElementById(btnId);

    if (btnObj == null) {
		alert("not found a button object\n"
				+ "[ button id : " + btnId + " ]");
		return false;
    }

    // 制御オブジェクト
    var ctrlObj = document.getElementById(ctrlId);

    if (ctrlObj == null) {
		alert("not found a control object\n"
				+ "[ control id : " + ctrlId + " ]");
		return false;
    }

    if (btnObj.value == dispBtnValue) {
        // 表示状態でボタンが押下された時

    	btnObj.value = nonDispBtnValue;
    	ctrlObj.style.display = "block";

    } else if (btnObj.value == nonDispBtnValue) {
        // 非表示状態でボタンが押下された時

    	btnObj.value = dispBtnValue;
    	ctrlObj.style.display = "none";

    } else {
        // 上記以外
        alert("a button value is not corresponding to \n"
                + "display button value or non-display button value\n"
        		+ "[ botton value : " + btnObj.value + " ]\n"
        		+ "[ display button value : " + dispBtnValue + " ]\n"
        		+ "[ non-display button value : " + nonDispBtnValue + " ]");
        return false;
    }
}

/**
 * 新規ウィンドウを起動する。
 *
 * @param form 起動時の転送フォームオブジェクト
 * @param width 新規ウィンドウの幅(pixels)
 * @param height 新規ウィンドウの高さ(pixels)
 */
function openWindow(form, width, height) {
    var newWin = window.open(
        "/reins/blank.html",
        "REINS",
        "width=" + width + ",height=" + height
        );
    form.target = "REINS";
    form.submit();
    newWin.focus();
}

// SY_0365 ADD Satoshi Koyanagi BEGIN
/**
 * ボタン押下時に非表示にされたオブジェクトを１秒後に表示を行う。
 *
 * @param btnId ボタンオブジェクトのID属性値
 *
 * setTimer(btnId)関数を利用する資材
 *  reins-online\webapps\WEB-INF\tiles\baseLayout.jsp
 *  reins-online\webapps\WEB-INF\tiles\baseLayout2.jsp
 *  reins-online\webapps\WEB-INF\tiles\childLayout.jsp
 *  reins-online\webapps\zmn\maskat\tiles\baseLayout.jsp
 */
function setTimer(btnName) {
	setTimeout(function(){document.getElementsByName(btnName)[0].disabled = false;},1000);
}
// SY_0365 ADD Satoshi Koyanagi END

/**
 * 図面を取得するボタン連続押し防止を行なう。
 * ボタンを非表示にし、サファリ以外のブラウザの場合指定秒数後にボタンを表示する。
 *
 * @param btnName ボタンオブジェクトのName属性値
 *
 */
function submitCheck(btnName){
    document.getElementsByName(btnName)[0].disabled = true;
    userA = navigator.userAgent;
    if(userA.indexOf("Safari") > -1){
        document.getElementsByName(btnName)[0].disabled = false;
        return false;
    }
    setTimer(btnName);
}
