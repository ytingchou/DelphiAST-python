program delphiast_parse_to_xml;

{$mode delphi}{$H+}

uses
  SysUtils,
  Classes,
  DelphiAST,
  DelphiAST.Classes,
  DelphiAST.Writer,
  SimpleParser.Lexer.Types;

type
  TIncludeHandler = class(TInterfacedObject, IIncludeHandler)
  strict private
    FDefaultPath: string;
    function NormalizeIncludeName(const S: string): string;
  public
    constructor Create(const DefaultPath: string);
    function GetIncludeFileContent(const ParentFileName, IncludeName: string;
      out Content: string; out FileName: string): Boolean;
  end;

constructor TIncludeHandler.Create(const DefaultPath: string);
begin
  inherited Create;
  FDefaultPath := IncludeTrailingPathDelimiter(DefaultPath);
end;

function TIncludeHandler.NormalizeIncludeName(const S: string): string;
var
  T: string;
begin
  T := Trim(S);
  if (Length(T) >= 2) and (((T[1] = #39) and (T[Length(T)] = #39)) or ((T[1] = #34) and (T[Length(T)] = #34))) then
    T := Copy(T, 2, Length(T) - 2);
  Result := T;
end;

function TIncludeHandler.GetIncludeFileContent(const ParentFileName, IncludeName: string;
  out Content: string; out FileName: string): Boolean;
var
  PathCandidate, NameOnly, BasePath: string;
  ContentList: TStringList;
begin
  NameOnly := NormalizeIncludeName(IncludeName);

  BasePath := ExtractFilePath(ParentFileName);
  if BasePath = '' then
    BasePath := FDefaultPath;

  PathCandidate := ExpandFileName(BasePath + NameOnly);
  if not FileExists(PathCandidate) then
    PathCandidate := ExpandFileName(FDefaultPath + NameOnly);

  if not FileExists(PathCandidate) then
    Exit(False);

  ContentList := TStringList.Create;
  try
    ContentList.LoadFromFile(PathCandidate);
    Content := ContentList.Text;
    FileName := PathCandidate;
    Result := True;
  finally
    ContentList.Free;
  end;
end;

function EscapeErrorText(const S: string): string;
begin
  Result := StringReplace(S, '|', '/', [rfReplaceAll]);
end;

var
  Builder: TPasSyntaxTreeBuilder;
  IncludeHandler: IIncludeHandler;
  InputFileName: string;
  InterfaceOnly: Boolean;
  Root: TSyntaxNode;
  Stream: TStringStream;
begin
  if ParamCount < 1 then
  begin
    WriteLn(ErrOutput, 'ERROR|0|0||Usage: delphiast_parse_to_xml <file> [--interface-only]');
    Halt(64);
  end;

  InputFileName := ExpandFileName(ParamStr(1));
  if not FileExists(InputFileName) then
  begin
    WriteLn(ErrOutput, 'ERROR|0|0||File not found: ', EscapeErrorText(InputFileName));
    Halt(66);
  end;

  InterfaceOnly := (ParamCount >= 2) and (ParamStr(2) = '--interface-only');

Stream := TStringStream.Create;
try
  try
    Stream.LoadFromFile(InputFileName);

    Builder := TPasSyntaxTreeBuilder.Create;
    try
      Builder.InterfaceOnly := InterfaceOnly;
      Builder.InitDefinesDefinedByCompiler;
      IncludeHandler := TIncludeHandler.Create(ExtractFilePath(InputFileName));
      Builder.IncludeHandler := IncludeHandler;

      Root := Builder.Run(Stream);
      try
        Write(TSyntaxTreeWriter.ToXML(Root, True));
      finally
        Root.Free;
      end;
    finally
      Builder.Free;
    end;
  except
    on E: ESyntaxTreeException do
    begin
      WriteLn(ErrOutput,
        'SYNTAX_ERROR|',
        E.Line,
        '|',
        E.Col,
        '|',
        EscapeErrorText(E.FileName),
        '|',
        EscapeErrorText(E.Message));
      Halt(2);
    end;
    on E: EParserException do
    begin
      WriteLn(ErrOutput,
        'SYNTAX_ERROR|',
        E.Line,
        '|',
        E.Col,
        '|',
        EscapeErrorText(E.FileName),
        '|',
        EscapeErrorText(E.Message));
      Halt(2);
    end;
    on E: Exception do
    begin
      WriteLn(ErrOutput, 'ERROR|0|0||', EscapeErrorText(E.Message));
      Halt(1);
    end;
  end;
finally
  Stream.Free;
end;
end.
