Public Class RegisterException
    Inherits Exception
End Class

Module Module1
    'This utility is compiled into two versions, 32 and 64 bit, which are called from sdna_unlock
    'On a 32-bit platform only the 32 bit version will run
    'on a 64-bit platform BOTH will run
    Function is64bit()
        Return IntPtr.Size = 8
    End Function

    Function sdnacomwrapperpath()
        If is64bit() Then
            Return "x64\sdnacomwrapper.dll"
        Else
            Return "sdnacomwrapper.dll"
        End If
    End Function

    Sub register_sdna()
        'sdnaprogressbar (.net assembly - anycpu - same executable both 32/64 bit)
        Dim rs = New System.Runtime.InteropServices.RegistrationServices()
        If Not rs.RegisterAssembly(System.Reflection.Assembly.LoadFrom("sdnaprogressbar.dll"), _
                                   System.Runtime.InteropServices.AssemblyRegistrationFlags.SetCodeBase) Then
            Throw New RegisterException
        End If

        'sdnacomwrapper (native assembly - compiled both 32 and 64 bit)
        'regsvr32.exe will be called correctly either as 32- or 64-bit through filesystem redirection
        Dim subproc As System.Diagnostics.Process = New System.Diagnostics.Process()
        subproc.StartInfo.FileName = "regsvr32"
        subproc.StartInfo.Arguments = "/s " + sdnacomwrapperpath()
        subproc.Start()
        subproc.WaitForExit()
        If Not subproc.ExitCode = 0 Then
            Throw New RegisterException
        End If
        subproc.Close()
    End Sub

    Sub unregister_sdna()
        'sdnaprogressbar (.net assembly - anycpu - same executable both 32/64 bit)
        Dim rs = New System.Runtime.InteropServices.RegistrationServices()
        If Not rs.UnregisterAssembly(System.Reflection.Assembly.LoadFrom("sdnaprogressbar.dll")) Then
            Throw New RegisterException
        End If

        'sdnacomwrapper (native assembly - compiled both 32 and 64 bit)
        'regsvr32.exe will be called correctly either as 32- or 64-bit through filesystem redirection
        Dim subproc As System.Diagnostics.Process = New System.Diagnostics.Process()
        subproc.StartInfo.FileName = "regsvr32"
        subproc.StartInfo.Arguments = "/u /s " + sdnacomwrapperpath()
        subproc.Start()
        subproc.WaitForExit()
        If Not subproc.ExitCode = 0 Then
            Throw New RegisterException
        End If
        subproc.Close()
    End Sub

    Sub main()
        'argument of "u" indicates unregister
        Dim register As Boolean = True
        For Each s As String In My.Application.CommandLineArgs
            If s = "u" Then
                register = False
            End If
        Next

        Try
            If register Then
                register_sdna()
            Else
                unregister_sdna()
            End If
        Catch ex As Exception
            Environment.Exit(1)
        End Try
    End Sub
End Module
