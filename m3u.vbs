Const ForReading = 1, ForWriting = 2, ForAppending = 8
 
' the full path to the folder you want to write the m3u's out to (must have trailing slash):
playlistPath = "C:\Users\rcrouch8147\Playlists\"
 
' the path which XBMC thinks your music is stored (must have trailing slash):
musicPath = "/media/media/music/"
 
' Parse command-line arguments
delete = false
set args = WScript.Arguments
if args.Count &gt; 0 then
    if LCase(args(0)) = "-d" then
        delete = true
    end if
end if
 
' Write m3u files for current directory tree
set fso = CreateObject("Scripting.FileSystemObject")
wscript.echo WriteM3u(fso.GetAbsolutePathName("."), delete) &amp; " files written"
 
' Recursive function to write m3u files for a given path
function WriteM3u(path, delete)
    count = 0
    set fso = CreateObject("Scripting.FileSystemObject")
    set fdr = fso.GetFolder(path)
     
    ' Write m3u file for each subfolder
    if fdr.SubFolders.Count &gt; 0 then
        for each subFolder in fdr.SubFolders
            count = count + WriteM3u(subFolder.path, delete)
        next
    end if
     
    ' If no files found in subfolders, write m3u file for this folder
    if count = 0 then
        ' wscript.echo "Scanning """ &amp; fdr.Path &amp; """"
        ' Build list of mp3/ogg files
        mp3List = ""
        for each f in fdr.Files
            if right(f.Name, 3) = "mp3" or right(f.Name, 3) = "ogg" then
               folderName = Replace(fdr.Name, " ", "\ ")
               fileName = Replace(f.Name, " ", "\ ")
               if fdr.ParentFolder.Name = "Music" then
                   mp3List = mp3List &amp; musicPath &amp; folderName &amp; "/" &amp; fileName &amp; VBCrLf
               else
                   mp3List = mp3List &amp; musicPath &amp; fdr.ParentFolder.Name &amp; folderName &amp; "/" &amp; fileName &amp; VBCrLf
               end if
            end if
        next
         
        ' If any files found, write m3u file
        if mp3List  "" then
            ' Multi-disc folder handling
            if fdr.ParentFolder.Name = "Music" Then
                folderName = Replace(fdr.Name, " ", "")
                m3uName = folderName &amp; ".m3u"           
            Else
                parentfolderName = Replace(fdr.ParentFolder.Name, " ", "")
                folderName = Replace(fdr.Name, " ", "")
                m3uName = parentfolderName &amp; folderName &amp; ".m3u"
            end if
             
            ' Existing m3u file handling
            m3u = playlistPath &amp; m3uName
            if fso.FileExists(m3u) then
                if delete then
                    ' wscript.echo "... deleting existing file"
                    fso.DeleteFile m3u
                else
                    ' wscript.echo "... renaming existing file"
                    fso.MoveFile m3u, m3u &amp; ".old"
                end if
            end if
             
            ' Write new m3u file
            ' wscript.echo "... writing """ &amp; m3uName &amp; """"
            set m3uFile = fso.OpenTextFile(m3u, ForWriting, True)
            m3uFile.Write(mp3List)
            m3uFile.Close
            count = 1
        else
            ' wscript.echo "... no mp3/ogg files found"
        end if
    end if
     
    ' Return m3u file count
    WriteM3u = count
end function