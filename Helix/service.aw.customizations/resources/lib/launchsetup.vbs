Dim objShell
Dim args
Set args = WScript.Arguments
Set objShell = WScript.CreateObject("WScript.Shell")
On Error Resume Next
ret = objShell.Run (Chr(34) & args.Item(0) & Chr(34) & " /S", 1,true)
Set objShell = Nothing
If Err.Number <> 0 Then
	WScript.Quit(Err.Number)
Else
	WScript.Quit(ret)
End If
