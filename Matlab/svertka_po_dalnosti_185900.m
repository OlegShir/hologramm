clc
fclose all
close all
clear all
% [FName_r, PathName_r]=uigetfile('*.rgg','Open File Rgg*','D:\MATLAB\RLI_2010\22_07_2010\_220710_RGGX\');
% if FName_r~=0
%     FullName_r=[PathName_r FName_r];
% end
FullName_r = num2str('I:\Matlab\Ivanovo_ChKP\_030613_185900X(VV)\03 06 13  18.59.00 X (VV).rgg');
Name = FullName_r;
% [�������� ������] = name_F(������� ������);
[Nd,Ndn,Nd2,dnr,c,lamb,Tpi,fcvant2,Nazim,Fsp,Dimp] = ish_dan_185900(Name);
N_otst=40000; %Nazim-Na;
Na=90000;
%+++ ���������� ��� ����������� ���������� �� ��������� +++
% razr_y=0.5;
% tr_razr_y=0.5;
% k=tr_razr_y/razr_y;
% N11=fix(N1/k); % ��� ����������� ��� �� ��������� ��������� ������������� ������ N1
% ++++++
 %====== ��������� �� ��� ������� ������������ �������� ============
 opor(Nd)=0; %Nd ������ ���-�� �������� = ������� ������, ����� ��� ����������� �������
 N1=fix(Dimp*fcvant2); % ����� �������� � ��������
 for n=1:1:N1
	faza=pi*Fsp*(n-1)^2/(N1*fcvant2) - pi*Fsp*(n-1)/fcvant2; %���� ������� ������� - 
	oc(n)=cos(faza); %cos ������������ ����
	os(n)=sin(faza); %sin ������������ ����
	opor(n)=complex(oc(n),os(n)); %������ ���� ������� � ����������� ����
 end
 opor2(Nd,1)=0;
 N2=fix(N1/2);
 for n=1:1:N2 %����� ������� ������� ��� ���������� ������ ����������� (�����) � ������� ��������
     opor2(n)=opor(n+N2);
     opor2(n+Nd-N2)=opor(n);
 end
 figure
 plot(imag(opor))
sp_OF=fft(opor2);
figure
 plot(abs(sp_OF))
clear opor opor2 oc os faza
%====================================================================
svRG(Nd)=0; %Nd ������ ���-�� �������� = ������� ������, ����� ��� ����������� �������
stc(Nd)=complex(0,0);
% ������ ��� �� �����
fid1=fopen(FullName_r);
h1=fseek(fid1,2*Ndn*N_otst,'bof');    
% % �������� ������������ ������
% figure
% hold on
% for i=1:1:10
%     st=fread(fid1,[Nd2],'uint8');
%     st = gt(st,128).*(st-256)+le(st,128).*st;% ��������� �������� �� -127 �� +128
%     stolb(:,i)=st;
%     plot(stolb(1:500,i))
% end
% pause(10)
% [FName_wr, PathName_wr]=uiputfile('','���������� ������ ���*','D:\MATLAB\RLI_2010\22_07_2010\_220710_RGGX\RGG_sv_dalnost\sv_142550');
% if FName_wr~=0
%     FullName_wr=[PathName_wr FName_wr];
% end
FullName_wr = num2str('I:\Matlab\Ivanovo_ChKP\_030613_185900X(VV)\sv_185900_IL18.rpt');
Name_wr = FullName_wr;
fid2=fopen(FullName_wr,'w+'); %��������� �� �������� ����, ������� ������ (��������)

a=0
for i=1:1:Na 
    st=fread(fid1,[Nd2],'uint8');
    st = gt(st,128).*(st-256)+le(st,128).*st;% ��������� �������� �� -127 �� +128
    st(1:128)=0;
    %�� ���������� ���-�� �������� ��������� ������ ������� � ����������� ����
    stc=complex( st(1:2:Nd2) , st(2:2:Nd2));
    stc(Ndn+1:Nd)=0;
    sp_stc=fft(stc);
    %������ ������� ������������ ������� � ���
    svRG=sp_stc.*sp_OF; %������������ �������� ������� �� ������� ������
    svRG=ifft(svRG); 
    Rg(1:Nd)=real(svRG);
    Rg(Nd+1:2*Nd)  =imag(svRG);
    h=fwrite(fid2,Rg,'float32');% ������ � ���� ������ 4 ����� ����� �����, 4 ����� ������ ����� �� ������� � ������ ���������
    a=a+1 %������� ��� ����������� ����������� ���������
end
clear svRG stc sp_stc svRG Rg st sp_OF
% 
% fid3=fopen(FullName_wr,'rb');
% clear rgg1
% Na_otst=25000;  
% Ndcentre=fix(Nd/2); 
% Ndrazmer=fix(Nd/2); 
% Ndv=Ndcentre-Ndrazmer/2;
% Ndniz=Ndcentre+Ndrazmer/2;
% Ndrz=Ndniz-Ndv;
% Na_read=30000;
% fseek(fid3,2*Nd*Na_otst*4+Ndv*4,'bof');
% read=0
% for i=1:1:Na_read
%     r1=fread(fid3,[Ndrz],'float32');
%     fseek(fid3,(Nd-Ndrz)*4,'cof');
%     r2=fread(fid3,[Ndrz],'float32');
%     fseek(fid3,(Nd-Ndrz)*4,'cof');
%     rgg1(:,i)=complex(r1,r2);
%     read=read+1
% end
% clear r1 r2
% fclose all
% figure
% h=image(real(rgg1)*0.0200000)
% colormap(gray);