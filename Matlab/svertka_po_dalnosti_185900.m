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
% [выходные данные] = name_F(входные данные);
[Nd,Ndn,Nd2,dnr,c,lamb,Tpi,fcvant2,Nazim,Fsp,Dimp] = ish_dan_185900(Name);
N_otst=40000; %Nazim-Na;
Na=90000;
%+++ Необходимо для загрубления разрешения по дальности +++
% razr_y=0.5;
% tr_razr_y=0.5;
% k=tr_razr_y/razr_y;
% N11=fix(N1/k); % При загрублении РЛИ по наклонной дальности подставляется вместо N1
% ++++++
 %====== Формируем ОФ для свертки зондирующего импульса ============
 opor(Nd)=0; %Nd больше кол-ва отсчетов = степени двойки, нужно для последующей свертки
 N1=fix(Dimp*fcvant2); % Число отсчетов в импульсе
 for n=1:1:N1
	faza=pi*Fsp*(n-1)^2/(N1*fcvant2) - pi*Fsp*(n-1)/fcvant2; %фаза опорной функции - 
	oc(n)=cos(faza); %cos состовляющая фазы
	os(n)=sin(faza); %sin состовляющая фазы
	opor(n)=complex(oc(n),os(n)); %отсчет фазы сигнала в комплексном виде
 end
 opor2(Nd,1)=0;
 N2=fix(N1/2);
 for n=1:1:N2 %сдвиг опорной функции для совмещения начала изображения (кадра) с началом отсчетов
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
svRG(Nd)=0; %Nd больше кол-ва отсчетов = степени двойки, нужно для последующей свертки
stc(Nd)=complex(0,0);
% Чтение РГГ из файла
fid1=fopen(FullName_r);
h1=fseek(fid1,2*Ndn*N_otst,'bof');    
% % Проверка правильности чтения
% figure
% hold on
% for i=1:1:10
%     st=fread(fid1,[Nd2],'uint8');
%     st = gt(st,128).*(st-256)+le(st,128).*st;% формируем значения от -127 до +128
%     stolb(:,i)=st;
%     plot(stolb(1:500,i))
% end
% pause(10)
% [FName_wr, PathName_wr]=uiputfile('','Сохранение сжатой РГГ*','D:\MATLAB\RLI_2010\22_07_2010\_220710_RGGX\RGG_sv_dalnost\sv_142550');
% if FName_wr~=0
%     FullName_wr=[PathName_wr FName_wr];
% end
FullName_wr = num2str('I:\Matlab\Ivanovo_ChKP\_030613_185900X(VV)\sv_185900_IL18.rpt');
Name_wr = FullName_wr;
fid2=fopen(FullName_wr,'w+'); %указатель на выходной файл, атрибут запись (дозапись)

a=0
for i=1:1:Na 
    st=fread(fid1,[Nd2],'uint8');
    st = gt(st,128).*(st-256)+le(st,128).*st;% формируем значения от -127 до +128
    st(1:128)=0;
    %Из удвоенного кол-ва отсчетов дальности делаем столбец в комплексном виде
    stc=complex( st(1:2:Nd2) , st(2:2:Nd2));
    stc(Ndn+1:Nd)=0;
    sp_stc=fft(stc);
    %Делаем свертку комплексного столбца и ОПФ
    svRG=sp_stc.*sp_OF; %перемножение спектров столбца на опорную фунцию
    svRG=ifft(svRG); 
    Rg(1:Nd)=real(svRG);
    Rg(Nd+1:2*Nd)  =imag(svRG);
    h=fwrite(fid2,Rg,'float32');% запись в файл строки 4 байта целая часть, 4 байта мнимая часть на элемент в канале дальности
    a=a+1 %счетчик для отображения прохождения программы
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