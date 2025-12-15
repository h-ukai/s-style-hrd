/*
*設備・条件入力ガイドの処理
* 2008/10/29 平田満 PT_0064
* 2009/03/11 劉宏博 KN_0021
*/
function HTMLDecode(text)
{
	var temp = document.createElement("div");
	temp.innerHTML = text;
	var output = temp.innerText || temp.textContent;
	temp = null;
	return output;
}
// 2008/09/01 劉宏博 SI1KK_BJ_0038対応 Begin
function openOptionNewWinSubmit (random, dtShri) {
// 2008/09/01 劉宏博 SI1KK_BJ_0038対応 End
    var bkknShbt;
    // 内部故障SI1KK_BK001_0028対応 MOD 関 2008/8/12 START
    bkknShbt = document.getElementsByName('bkknShbt1')[0].value;
    bkknShbt = bkknShbt + "," + document.getElementsByName('bkknShbt2')[0].value
    // 内部故障SI1KK_BK001_0028対応 MOD 関 2008/8/12 END
    // 2008/09/01 劉宏博 SI1KK_BJ_0038対応 Begin
    // var newWin = window.open('', 'InputGuideWindow', '');
	var feature
	var pos;
	var width=800;
	var height=600;

    pos="width="+width+",height="+height+",left="+(window.screen.width-width)/2 + ",top="+(window.screen.height-height)/2;
   	feature =pos+",menubar=no,toolbar=no,location=no,"; 
	feature+="scrollbars=yes,resizable=yes,status=no,modal=yes";
    
	//var newWin = window.open('', 'InputGuideWindow', feature);
	// 2008/10/29 平田満 PT_0064 START
	//var newWin = window.open('', 'win', feature);
	var newWin = window.open('/reins/blank.html', 'win', feature);
	// 2008/10/29 平田満 PT_0064 END
    // 2008/09/01 劉宏博 SI1KK_BJ_0038対応 End

    newWin.document.write('<html>');
    newWin.document.write('<body>');
    // 2009/03/11 劉宏博 KN_0021 Begin
    // newWin.document.write('<form id="BkknForm" name="BkknForm" action="/reins/bkkn/BK000_222.do');
    newWin.document.write('<form id="BkknForm" name="BkknForm" action="/reins/bkkn/BK001_222.do');
    // 2009/03/11 劉宏博 KN_0021 End
    
    newWin.document.write('?r=');
    newWin.document.write(random);
    newWin.document.write('" method="post">');

    newWin.document.write('<input type="hidden" name="dtShri" value="');
    newWin.document.write(dtShri);
    newWin.document.write('" />');

    newWin.document.write('<input type="hidden" name="bkknShbt" value="');
    newWin.document.write(bkknShbt);
    newWin.document.write('"/>');
    
    // 2008/09/01 劉宏博 SI1KK_BJ_0038対応 Begin
    //newWin.document.write('<input type="hidden" name="strStbJok" value="');
    //newWin.document.write(strStbJok);    
    newWin.document.write('<input type="hidden" name="optId" value="');
    newWin.document.write(this.document.forms[0].strStbJok.value);
    // 2008/09/01 劉宏博 SI1KK_BJ_0038対応 End
    newWin.document.write('"/>');
    
    newWin.document.write('</form>');
    newWin.document.write('</body>');
    newWin.document.write('</html>');
    
    var frm = newWin.document.getElementById('BkknForm');
    frm.submit();
    // 2008/09/01 劉宏博 SI1KK_BJ_0038対応 Begin
    newWin.focus();
    // 2008/09/01 劉宏博 SI1KK_BJ_0038対応 End
}

function setReturnValue(optId, optName) {
	window.document.getElementById("optId").value = optName;
	window.document.getElementById("strStbJok").value = optId;
}

/*
*物件種目リストの設定
*/
function displayChoose() {
	var bkknShbt1 = document.getElementsByName("bkknShbt1")[0].value;
	var bkknShmk1 = document.getElementsByName("bkknShmk1")[0].value;
	var bkknShbt2 = document.getElementsByName("bkknShbt2")[0].value;
	var bkknShmk2 = document.getElementsByName("bkknShmk2")[0].value;
	var bkknShmkList1 = document.getElementById("bkknShmkList1");
	var bkknShmkList2 = document.getElementById("bkknShmkList2");
	var bkknShmkList3 = document.getElementById("bkknShmkList3");
	var bkknShmkList4 = document.getElementById("bkknShmkList4");
	var bkknShmkList5 = document.getElementById("bkknShmkList5");
	var bkknShmkList6 = document.getElementById("bkknShmkList6");
	var bkknShmkList7 = document.getElementById("bkknShmkList7");
	var bkknShmkList8 = document.getElementById("bkknShmkList8");
	var bkknShmkList9 = document.getElementById("bkknShmkList9");
	var bkknShmkList10 = document.getElementById("bkknShmkList10");
	// 2008/11/06 関 SI3_NT_0268 Begin
	var bkknShmkList0 = document.getElementById("bkknShmkList0");
	var bkknShmkList11 = document.getElementById("bkknShmkList11");
	// 2008/11/06 関 SI3_NT_0268 End
	
	bkknShmkList1.style.display = "none";
	bkknShmkList2.style.display = "none";
	bkknShmkList3.style.display = "none";
	bkknShmkList4.style.display = "none";
	bkknShmkList5.style.display = "none";
	bkknShmkList6.style.display = "none";
	bkknShmkList7.style.display = "none";
	bkknShmkList8.style.display = "none";
	bkknShmkList9.style.display = "none";
	bkknShmkList10.style.display = "none";
	// 2008/11/06 関 SI3_NT_0268 Begin
	bkknShmkList0.style.display = "none";
	bkknShmkList11.style.display = "none";
	// 2008/11/06 関 SI3_NT_0268 End
		
	if (bkknShbt1 == 02) {
		document.forms[0].bkknShmkDispList1[1].value = bkknShmk1;
		bkknShmkList2.style.display = "";
	} else if (bkknShbt1 == 03) {
		document.forms[0].bkknShmkDispList1[2].value = bkknShmk1;
		bkknShmkList3.style.display = "";
	} else if (bkknShbt1 == 04) {
		document.forms[0].bkknShmkDispList1[3].value = bkknShmk1;
		bkknShmkList4.style.display = "";
	} else if (bkknShbt1 == 05) {
		document.forms[0].bkknShmkDispList1[4].value = bkknShmk1;
		bkknShmkList5.style.display = "";
	// 2008/11/06 関 SI3_NT_0268 Begin
	} else if (bkknShbt1 == 01) {
		document.forms[0].bkknShmkDispList1[0].value = bkknShmk1;
		bkknShmkList1.style.display = "";
	} else {
		document.forms[0].bkknShmkDispList1[5].value = bkknShmk1;
		bkknShmkList0.style.display = "";
	}
	// 2008/11/06 関 SI3_NT_0268 End
	if (bkknShbt2 == 02) {
		document.forms[0].bkknShmkDispList2[1].value = bkknShmk2;
		bkknShmkList7.style.display = "";
	} else if (bkknShbt2 == 03) {
		document.forms[0].bkknShmkDispList2[2].value = bkknShmk2;
		bkknShmkList8.style.display = "";
	} else if (bkknShbt2 == 04) {
		document.forms[0].bkknShmkDispList2[3].value = bkknShmk2;
		bkknShmkList9.style.display = "";
	} else if (bkknShbt2 == 05) {
		document.forms[0].bkknShmkDispList2[4].value = bkknShmk2;
		bkknShmkList10.style.display = "";
	// 2008/11/06 関 SI3_NT_0268 Begin
	} else if (bkknShbt2 == 01) {
		document.forms[0].bkknShmkDispList2[0].value = bkknShmk2;
		bkknShmkList6.style.display = "";
	} else {
		document.forms[0].bkknShmkDispList2[5].value = bkknShmk2;
		bkknShmkList11.style.display = "";
	}
	// 2008/11/06 関 SI3_NT_0268 End
}

function displayChooseWithValue(index) {
	var bkknShbt1 = document.getElementsByName("bkknShbt1")[0].value;
	var bkknShbt2 = document.getElementsByName("bkknShbt2")[0].value;
	var bkknShmkList1 = document.getElementById("bkknShmkList1");
	var bkknShmkList2 = document.getElementById("bkknShmkList2");
	var bkknShmkList3 = document.getElementById("bkknShmkList3");
	var bkknShmkList4 = document.getElementById("bkknShmkList4");
	var bkknShmkList5 = document.getElementById("bkknShmkList5");
	var bkknShmkList6 = document.getElementById("bkknShmkList6");
	var bkknShmkList7 = document.getElementById("bkknShmkList7");
	var bkknShmkList8 = document.getElementById("bkknShmkList8");
	var bkknShmkList9 = document.getElementById("bkknShmkList9");
	var bkknShmkList10 = document.getElementById("bkknShmkList10");
	// 2008/11/06 関 SI3_NT_0268 Begin
	var bkknShmkList0 = document.getElementById("bkknShmkList0");
	var bkknShmkList11 = document.getElementById("bkknShmkList11");
	// 2008/11/06 関 SI3_NT_0268 End
	
	bkknShmkList1.style.display = "none";
	bkknShmkList2.style.display = "none";
	bkknShmkList3.style.display = "none";
	bkknShmkList4.style.display = "none";
	bkknShmkList5.style.display = "none";
	bkknShmkList6.style.display = "none";
	bkknShmkList7.style.display = "none";
	bkknShmkList8.style.display = "none";
	bkknShmkList9.style.display = "none";
	bkknShmkList10.style.display = "none";
	// 2008/11/06 関 SI3_NT_0268 Begin
	bkknShmkList0.style.display = "none";
	bkknShmkList11.style.display = "none";
	// 2008/11/06 関 SI3_NT_0268 End
	
		
	if (bkknShbt1 == 02) {
	    if (1 == index) {
			document.forms[0].bkknShmkDispList1[1].selectedIndex = 0;
			document.forms[0].bkknShmk1.value = ""
		} else {
			document.forms[0].bkknShmkDispList2[1].selectedIndex = 0;
			document.forms[0].bkknShmk2.value = ""
		}
		bkknShmkList2.style.display = "";
	} else if (bkknShbt1 == 03) {
		if (1 == index) {
			document.forms[0].bkknShmkDispList1[2].selectedIndex = 0;
			document.forms[0].bkknShmk1.value = ""
		} else {
			document.forms[0].bkknShmkDispList2[2].selectedIndex = 0;
			document.forms[0].bkknShmk2.value = ""
		}
		bkknShmkList3.style.display = "";
	} else if (bkknShbt1 == 04) {
		if (1 == index) {
			document.forms[0].bkknShmkDispList1[3].selectedIndex = 0;
			document.forms[0].bkknShmk1.value = ""
		} else {
			document.forms[0].bkknShmkDispList2[3].selectedIndex = 0;
			document.forms[0].bkknShmk2.value = ""
		}
		bkknShmkList4.style.display = "";
	} else if (bkknShbt1 == 05) {
		if (1 == index) {
			document.forms[0].bkknShmkDispList1[4].selectedIndex = 0;
			document.forms[0].bkknShmk1.value = ""
		} else {
			document.forms[0].bkknShmkDispList2[4].selectedIndex = 0;
			document.forms[0].bkknShmk2.value = ""
		}
		bkknShmkList5.style.display = "";
	// 2008/11/06 関 SI3_NT_0268 Begin
	} else if (bkknShbt1 == 01) {
		if (1 == index) {
			document.forms[0].bkknShmkDispList1[0].selectedIndex = 0;
			document.forms[0].bkknShmk1.value = ""
		} else {
			document.forms[0].bkknShmkDispList2[0].selectedIndex = 0;
			document.forms[0].bkknShmk2.value = ""
		}
		bkknShmkList1.style.display = "";
	} else {
		if (1 == index) {
			document.forms[0].bkknShmkDispList1[5].selectedIndex = 0;
			document.forms[0].bkknShmk1.value = ""
		} else {
			document.forms[0].bkknShmkDispList2[5].selectedIndex = 0;
			document.forms[0].bkknShmk2.value = ""
		}
		bkknShmkList0.style.display = "";
	}
	// 2008/11/06 関 SI3_NT_0268 End
	
	if (bkknShbt2 == 02) {
		if (1 == index) {
			document.forms[0].bkknShmkDispList1[1].selectedIndex = 0;
			document.forms[0].bkknShmk1.value = ""
		} else {
			document.forms[0].bkknShmkDispList2[1].selectedIndex = 0;
			document.forms[0].bkknShmk2.value = ""
		}
		bkknShmkList7.style.display = "";
	} else if (bkknShbt2 == 03) {
		if (1 == index) {
			document.forms[0].bkknShmkDispList1[2].selectedIndex = 0;
			document.forms[0].bkknShmk1.value = ""
		} else {
			document.forms[0].bkknShmkDispList2[2].selectedIndex = 0;
			document.forms[0].bkknShmk2.value = ""
		}
		bkknShmkList8.style.display = "";
	} else if (bkknShbt2 == 04) {
		if (1 == index) {
			document.forms[0].bkknShmkDispList1[3].selectedIndex = 0;
			document.forms[0].bkknShmk1.value = ""
		} else {
			document.forms[0].bkknShmkDispList2[3].selectedIndex = 0;
			document.forms[0].bkknShmk2.value = ""
		}
		bkknShmkList9.style.display = "";
	} else if (bkknShbt2 == 05) {
		if (1 == index) {
			document.forms[0].bkknShmkDispList1[4].selectedIndex = 0;
			document.forms[0].bkknShmk1.value = ""
		} else {
			document.forms[0].bkknShmkDispList2[4].selectedIndex = 0;
			document.forms[0].bkknShmk2.value = ""
		}
		bkknShmkList10.style.display = "";
	// 2008/11/06 関 SI3_NT_0268 Begin
	} else if (bkknShbt2 == 01) {
		if (1 == index) {
			document.forms[0].bkknShmkDispList1[0].selectedIndex = 0;
			document.forms[0].bkknShmk1.value = ""
		} else {
			document.forms[0].bkknShmkDispList2[0].selectedIndex = 0;
			document.forms[0].bkknShmk2.value = ""
		}
		bkknShmkList6.style.display = "";
	} else {
		if (1 == index) {
			document.forms[0].bkknShmkDispList1[5].selectedIndex = 0;
			document.forms[0].bkknShmk1.value = ""
		} else {
			document.forms[0].bkknShmkDispList2[5].selectedIndex = 0;
			document.forms[0].bkknShmk2.value = ""
		}
		bkknShmkList11.style.display = "";
	}
	// 2008/11/06 関 SI3_NT_0268 End
}

function getSelectedValue(selectName,fieldName) {
		var bkknShmk = selectName.value;
		fieldName.value = bkknShmk;
}

/*
*検索入力画面項目のリセット
*/
function openOptionClearSubmit () {
	document.forms[0].reset(); 
}

/*
*設備・条件のリセット
*/
function openOptionClearStbJokSubmit () {
	window.document.getElementById("strStbJok").value = "";
	window.document.getElementById("optId").value = "";
}

// 故障SI2_NT_0571対応 MOD 関 2008/08/25 START
// 故障SI2_NT_0670,671,672対応 MOD 関 2008/09/01 START
/*
*会員詳細画面へ遷移する
*/
function openKainInfo(url, kiinId, gmnKbn,selectKiinBngu, random) {
	// 2008/10/29 平田満 PT_0064 START
	//var newWin = window.open('', 'win', feature);
    //var newWin = window.open('', 'windowName', 'location=0,menubar=0,toolbar=0,resizable=1,scrollbars=1,status=1');
    var newWin = window.open('/reins/blank.html', 'windowName', 'location=0,menubar=0,toolbar=0,resizable=1,scrollbars=1,status=1');
	// 2008/10/29 平田満 PT_0064 END
    newWin.document.write('<html>');
    newWin.document.write('<body>');
    newWin.document.write('<form id="childForm" name="childForm" action="');

    newWin.document.write(url);
    newWin.document.write('?r=');
    newWin.document.write(random);
    newWin.document.write('" method="post">');

    newWin.document.write('<input type="hidden" name="kiinId" value="');
    newWin.document.write(kiinId);
    newWin.document.write('" />');
    newWin.document.write('<input type="hidden" name="gmnKbn" value="');
    newWin.document.write(gmnKbn);
    newWin.document.write('" />');
    newWin.document.write('<input type="hidden" name="selectKiinBngu" value="');
    newWin.document.write(selectKiinBngu);
    newWin.document.write('" />');

    newWin.document.write('</form>');
    newWin.document.write('</body>');
    newWin.document.write('</html>');
    
    var frm = newWin.document.getElementById('childForm');
    frm.submit();

    return newWin;
}
// 故障SI2_NT_0670,671,672対応 MOD 関 2008/09/01 END
// 故障SI2_NT_0571対応 MOD 関 2008/08/25 END



/**
 * 非表示領域項目の入力有無による、画面表示／非表示切替機能。<br />
 * 物件検索のその他検索項目専用
 * 
 * changeDisplayと同一引数
 *
 * @auther kitagawa
 * @param id imgタグのID
 * @param hiddenId 非表示対象のID 
 * @param imgPth1 表示画像1
 * @param imgPth2 表示画像2
 */

function bk001_001_hideTableChiledNodeValue(image_Id, table_Id ,on_img_Path, off_img_Path){

    var openflg = false ;

    var hideTableEle = document.getElementById(table_Id);
    
    if ( hideTableEle != null ) {

        // select タグ属性の入力有無判定
        var selectTags = hideTableEle.getElementsByTagName("select");
        openflg = bk001_001_checkSelectElementSetValue( selectTags ) ;

        if ( openflg == false ) {
            // input タグ属性の入力有無判定
            var inputTags = hideTableEle.getElementsByTagName("input");
            openflg = bk001_001_checkInputElementSetValue(inputTags) ;
        }

        // 入力値有と判断した場合は、hidetagを開く
        if ( openflg ) {
            changeDisplay(image_Id, table_Id , on_img_Path, off_img_Path )
        }

    }

}

/**
 * 非表示領域項目の入力有無による、画面表示／非表示切替機能。<br />
 * ■selectタグ属性判定部■<br />
 * selectタグエレメントの要素をinputに <br />
 * selectedIndexの値が、平成「H」以外の場合は、デフォルト値以外が選択されている<br />
 * と判断し、trueを返却<br />
 * selectedIndexが平成「H」の場合は、デフォルト値が選択されている<br />
 * と判断し、falseを返却<br />
 * <br />
 * 
 * @auther kitagawa
 * @param selectTags selectタグエレメント要素
 */


function bk001_001_checkSelectElementSetValue( selectTags ) {
    for (var i = 0; i < selectTags.length; i++ ) {
        // 平成（H）以外が選択されていたら、表示切替
        if ( selectTags[i].value != 'H' ) return true ;
    }

    return false ;
}

/**
 * 非表示領域項目の入力有無による、画面表示／非表示切替機能。<br />
 * ■inputタグ属性判定部■<br />
 * inputタグエレメントの要素でvalue属性に値が存在する場合には<br />
 * 入力データ有と判断し、trueを返却<br />
 * inputタグエレメントの要素でvalue属性に値が存在しない場合には<br />
 * 入力データ有と判断し、falseを返却<br />
 * <br />
 * <br />
 * 
 * @auther kitagawa
 * @param inputTags inputタグエレメント要素
 */

function bk001_001_checkInputElementSetValue( inputTags ) {
    for (var i = 0; i < inputTags.length; i++ ) {
        switch (inputTags[i].type) {
            case 'text' :
                if ( inputTags[i].value.length > 0 ) return true ;
                break ;

            case 'radio' :
                if ( inputTags[i].checked ) {
                    if( inputTags[i].value != 1 ) return true ;
                }
                break ;

            case 'checkbox' :
            case 'password' :
            case 'file' :
            case 'submit' :
            case 'reset' :
            case 'hidden' :
            case 'image' :
            case 'button' :
            default :
        }
    }

    return false ;
}
function doSubmit(toWhere) {
	window.document.forms[0].event.value = toWhere;
	submitFirst();
}
// 故障 SI1_BK_0064対応 平田満　20081029 START
function doCSVDownload(toWhere) {

	var temp = "ＣＳＶをダウンロードします。\n連続してダウンロードするときは検索条件入力画面を再表示して\nダウンロード可能件数を確認してください。";
	
    if(confirm(temp)){
	    var frm = document.forms[0];
	    if (frm == null) {
			return false;
	    }
		frm.event.value = toWhere;
	    frm.submit();
    }
    return false;
}
// 故障 SI1_BK_0064対応 平田満　20081029 END

function openDownLoad(url, bkknId, random, kduFlg) {
	if (!submitFlg) {
		submitFlg = true;
		openPdfDownLoad(url, bkknId, random, kduFlg);
	}
}

// 故障SI1_BK_0042対応 MOD 関朋軍　20080911 START
function hideTableDisplay() {
	var btn_input_on_img = HTMLDecode(document.getElementById('contextPath').value) +  "/img/btn_input_on.gif";
	var btn_input_off_img = HTMLDecode(document.getElementById('contextPath').value) +  "/img/btn_input_off.gif";
	var btn_onetouch_input_on_img = HTMLDecode(document.getElementById('contextPath').value) +  "/img/btn_onetouch_input_on.gif";
	var btn_onetouch_input_off_img = HTMLDecode(document.getElementById('contextPath').value) +  "/img/btn_onetouch_input_off.gif";
	
    //hideTableChiledNodeValue('kkkuCnryuMnsk','hideTable3','${pageContext.request.contextPath}/img/btn_input_on.gif','${pageContext.request.contextPath}/img/btn_input_off.gif');
    hideTableChiledNodeValue('kkkuCnryuMnsk','hideTable3',btn_input_on_img,btn_input_off_img);
    
    //hideTableChiledNodeValue('shzicEnsn1','hideTable1','${pageContext.request.contextPath}/img/btn_input_on.gif','${pageContext.request.contextPath}/img/btn_input_off.gif');
    hideTableChiledNodeValue('shzicEnsn1','hideTable1',btn_input_on_img,btn_input_off_img);
    
    //hideTableChiledNodeValue('shzicEnsn2','hideTable2','${pageContext.request.contextPath}/img/btn_input_on.gif','${pageContext.request.contextPath}/img/btn_input_off.gif');
    hideTableChiledNodeValue('shzicEnsn2','hideTable2',btn_input_on_img,btn_input_off_img);
// 故障SI1_BK_0504対応 平田満　20080930 START
    var flg = document.getElementById("seniMotFlg").value;
    if (flg != 1){
        //hideTableChiledNodeValue('upperButton_bk001','hideTable14','${pageContext.request.contextPath}/img/btn_onetouch_input_on.gif','${pageContext.request.contextPath}/img/btn_onetouch_input_off.gif');
    	hideTableChiledNodeValue('upperButton_bk001','hideTable14',btn_onetouch_input_on_img,btn_onetouch_input_off_img);
    } else {
        // changeDisplay('upperButton_bk001', 'hideTable14','${pageContext.request.contextPath}/img/btn_onetouch_input_on.gif','${pageContext.request.contextPath}/img/btn_onetouch_input_off.gif');
        changeDisplay('upperButton_bk001', 'hideTable14',btn_onetouch_input_on_img,btn_onetouch_input_off_img);
    } 
    document.getElementById("seniMotFlg").value = "";
// 故障SI1_BK_0504対応 平田満　20080930 END
	// bk001_001_hideTableChiledNodeValue('optSnt','hideTable25','${pageContext.request.contextPath}/img/btn_input_on.gif','${pageContext.request.contextPath}/img/btn_input_off.gif');
	bk001_001_hideTableChiledNodeValue('optSnt','hideTable25',btn_input_on_img,btn_input_off_img);
}
// 故障SI1_BK_0042対応 MOD 関朋軍　20080911 END