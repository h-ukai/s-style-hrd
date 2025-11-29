/*
 * 2008/07/29 田 仕様変更の修正 課題管理簿（北京⇒NTTD）No302
 * 2008/09/03 田 SI2_NT_0671 横展開対応
 * 2008/10/07 星勝也 SI2_NT_0446
 * 2008/10/29 平田満 PT_0064
 */

function openZmnUpload(showDialog, showMessage,logicFileField,physicalFileFierd,url, random)
{
	var feature
	var pos;
	var width=800;
	var height=600;
	
	if(1 == showDialog){
		// SI2_NT_010 20080812 begin
		if( ! window.confirm(showMessage) ){
		 	return false;
		 }
		// alert(showMessage);
		// SI2_NT_010 20080812 END
	}
	pos="width="+width+",height="+height+",left="+(window.screen.width-width)/2 + ",top="+(window.screen.height-height)/2;
   	feature =pos+",menubar=no,toolbar=no,location=no,"; 
   	// SI2_NT_0446 MOD 星勝也 BEGIN
	// feature+="scrollbars=yes,resizable=yes,status=no,modal=yes";
	feature+="scrollbars=yes,resizable=yes,status=yes,modal=yes";
	// SI2_NT_0446 MOD 星勝也 END
	// 2008/10/29 平田満 PT_0064 START
	var newWin = window.open('/reins/blank.html', null, feature);
	//var newWin = window.open('', null, feature);
	// 2008/10/29 平田満 PT_0064 END

    newWin.document.write('<html>');
    newWin.document.write('<body>');
    newWin.document.write('<form id="Bkkn" action="');
    newWin.document.write(url);

    newWin.document.write('?r=');
    newWin.document.write(random);
    newWin.document.write('" method="post">');

    newWin.document.write('<input type="hidden" name="logicFileField" value="');
    newWin.document.write(logicFileField);
    newWin.document.write('" />');

    newWin.document.write('<input type="hidden" name="physicalFileFierd" value="');
    newWin.document.write(physicalFileFierd);
    newWin.document.write('"/>');

    newWin.document.write('</form>');
    newWin.document.write('</body>');
    newWin.document.write('</html>');
    var frm = newWin.document.getElementById('Bkkn');
    frm.submit();
}

// 2008/07/29 田 仕様変更の修正 Begin
function openMapInfoWindow(code) {
  
  var features = "width=900,height=600,menubar=1,toolbar=1,location=1,scrollbars=1,resizable=1"

  if (code.length > 0) {
    window.open(code , "", features);
  } 
}
// 2008/07/29 田 仕様変更の修正 End

function openOptionNewWinSubmit (path, random, dtShri, bkknShbt) {

	var feature
	var pos;
	var width=800;
	var height=600;
	
	// 設備・条件 入力ガイド
    pos="width="+width+",height="+height+",left="+(window.screen.width-width)/2 + ",top="+(window.screen.height-height)/2;
   	feature =pos+",menubar=no,toolbar=no,location=no,"; 
	feature+="scrollbars=yes,resizable=yes,status=no,modal=yes";	
	// 2008/08/13 田 BUG対応 Begin
	var newWin = window.open('/reins/blank.html', 'win', feature);
    // 2008/08/13 田 BUG対応 End
    
    newWin.document.write('<html>');
    newWin.document.write('<body>');
    newWin.document.write('<form id="BkknMntForm" name="BkknMntForm" action="');
    newWin.document.write(path);
    
    newWin.document.write('?r=');
    newWin.document.write(random);
    newWin.document.write('" method="post">');

    newWin.document.write('<input type="hidden" name="dtShri" value="');
    newWin.document.write(dtShri);
    newWin.document.write('" />');

    newWin.document.write('<input type="hidden" name="bkknShbt" value="');
    newWin.document.write(bkknShbt);
    newWin.document.write('"/>');
    
    newWin.document.write('<input type="hidden" name="optId" value="');
    newWin.document.write(this.document.forms[0].optId.value);
    newWin.document.write('"/>');
    
    newWin.document.write('</form>');
    newWin.document.write('</body>');
    newWin.document.write('</html>');
    var frm = newWin.document.getElementById('BkknMntForm');
    frm.submit();
    
    // 2008/08/13 田 BUG対応 Begin
    newWin.focus();
    // 2008/08/13 田 BUG対応 End
}

function openOptionClearSubmit () {
    document.forms[0].optId.value="";
	window.document.getElementById("optKnskName").value = "";
}

function setReturnValue(optId, optName) {

    document.forms[0].optKnskName.value = optName;
    document.forms[0].optId.value = optId;
    
	window.document.getElementById("optKnskName").value = optName;
	window.document.getElementById("optId").value = optId;
}

// 2008/09/03 田 SI2_NT_0671 横展開対応 Begin
function openKiinInfo(url, kiinId, gmnKbn, random) {
	// 2008/10/29 平田満 PT_0064 START
    var newWin = window.open('/reins/blank.html', 'windowName', 'location=0,menubar=0,toolbar=0,resizable=1,scrollbars=1,status=1');
    //var newWin = window.open('', 'windowName', 'location=0,menubar=0,toolbar=0,resizable=1,scrollbars=1,status=1');
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
// 2008/09/03 田 SI2_NT_0671 横展開対応 End
    newWin.document.write('</form>');
    newWin.document.write('</body>');
    newWin.document.write('</html>');
    
    var frm = newWin.document.getElementById('childForm');
    frm.submit();

    return newWin;
}