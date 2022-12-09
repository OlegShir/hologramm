clc
fclose all
close all
clear all

% [FileName, PathName]=uigetfile('*.rpt','Открытие сжатой по дальности РГГ','D:\MATLAB\RLI_2010\22_07_2010\_220710_RGGX\RGG_sv_dalnost\');
% if FileName~=0
%     FullName=[PathName FileName];
% end
FullName = num2str('I:\Matlab\Ivanovo_ChKP\_030613_185900X(VV)\sv_185900_IL18.rpt');
Name = FullName;

% [выходные данные] = name_F(входные данные);
% name = num2str('D:\MATLAB\Ivanovo\_030613_185900X\sv_dal\sv_185900.rgg');

[Nd,Ndn,Nd2,dnr,c,lamb,Tpi,fcvant2,Nazim,Fsp,Dimp] = ish_dan_185900(Name)
Na_otst=23000;   %8000 - УО и самолеты;
Ndcentre=5000; %8500;   % Nd/2
Ndrazmer=2000; %4000;  
Ndv=Ndcentre-Ndrazmer/2;%6050;  %6050
Ndniz=Ndcentre+Ndrazmer/2;%6306;  %6306
Ndrz=Ndniz-Ndv;
Na=15000; %65536;  % размер по азимуту
% % в _030613_185900X при АФ по УО V0 = 108 м/с; 
V0 = 108;
dx = V0*Tpi;
dx0 = dx;
R=4180; % 3995 - до нижнего УО Х-диапазона; 4180 - до самолетов
resol=0.4;
Nas=fix(lamb*R/2/resol/dx);
Nas = fix(Nas/2)*2;
rgg1=zeros(Ndrz,Na);
Porog = 0.7;


% Чтение свернутой по дальности РГГ
fid1=fopen(Name,'rb');
fseek(fid1,2*Nd*Na_otst*4+Ndv*4,'bof');
read=0
for i=1:1:Na
    r1=fread(fid1,[Ndrz],'float32');
    fseek(fid1,(Nd-Ndrz)*4,'cof');
    r2=fread(fid1,[Ndrz],'float32');
    fseek(fid1,(Nd-Ndrz)*4,'cof');
    rgg1(:,i)=complex(r1,r2);
    read=read+1
end
clear r1 r2
fclose all
Mashtab = 0
if Mashtab~=1
   Kx=1; Ky=1;
elseif Mashtab==1
% Масштабирование РГГ (приводим к квадратному пикселу)
piks=0.25;
sprgg1=fft2(rgg1); 
clear rgg1
Kx = piks/dx;  % Коэф-т переквантования РГГ по азимуту
Ky = dnr/piks; % Коэф-т переквантования РГГ по дальности
Naa2 = fix(Na/Kx/2);
Ndrz2=fix(Ndrz*Ky/2)*2;
Nd_zeros(Ndrz2-Ndrz,Naa2*2)=zeros;
% Урезаем спектр РГГ по азимуту
sp_rgg01(:,1:Naa2) = sprgg1(:,1:Naa2);
sp_rgg01(:,Naa2+1:Naa2*2) = sprgg1(:,Na-Naa2+1:end);
clear sprgg1
% Раздвигаем спектр по наклонной дальности
sp_rgg01 = [sp_rgg01(1:Ndrz/2,:);Nd_zeros;sp_rgg01(Ndrz/2+1:Ndrz,:)];
% Теперь шаг по обеим координатам один и равен величине piks
dx=piks;
dnr=piks;
rgg1=ifft2(sp_rgg01);
clear sp_rgg01
end
% figure
% h=image(real(rgg1)*0.02);
% title('РГГ, свернутая по дальности')
% colormap(gray);
[Ndrz0 Na0]=size(rgg1);
Absrgg1=abs(rgg1);
% Вычитаем постоянную составляющую
rg_sum=zeros(1,Na0); 
rg_sum=sum(rgg1);
sr_rg_sum = mean(rg_sum);
for n=1:1:Ndrz0
    rgg1(n,:)=rgg1(n,:)-sr_rg_sum/Ndrz0;
end
% % Определение минимальной наклонной дальности на изображении
R_UO = R; %R; % 
N_UO = 1267; % Номер строки в нашем РЛИ с УО на дальности R_UO
% R_UO = 6973; %R; % 
% N_UO = fix(586*Ky); % Номер строки в нашем РЛИ с УО на дальности R_UO
Rmin = R_UO-(N_UO-1)*dnr;
Rmax = Rmin+Ndrz0*dnr;
Rsr = R_UO;%(Rmax+Rmin)/2;
Nas_max=fix(lamb*Rmax/2/resol/dx);
% +++++++ Оцениваем по РГГ снос +++++++++++
Rsr = R_UO;
[N_snos_sr, Ugol_snosa, a0] = Funct_opredel_ugla_snosa(rgg1,Rsr,dx,lamb);
% Если alfa=Ugol_snosa, то при синтезе используется снос,...
        ...если alfa=0, то влияние сноса при синтезе не учитывается
% alfa = Ugol_snosa
alfa = Ugol_snosa;%Ugol_snosa;
N_snos_x = fix(tan(alfa*pi/180)*Rmin/dx);
% N_snos_x = 0; %-N_snos_sr;
dsm0=N_snos_x; %N_snos_x;
% +++++++++++++++++++++++++++++++++++++++++
% Определим предельную величину высоты блока в метрах
Ls_sr = fix(lamb*Rmin/(2*resol));
dR = lamb*(Rsr/(Ls_sr+2*abs(N_snos_x)*dx))^2; % Предельная высота блока в метрах
Ndr = 2; %fix(dR/dnr);      % Высота блока в отсчетах (по изображению)
Nbl_r = fix(Ndrz0/Ndr) % Кол-во разбиений (блоков) по наклонной дальности
% --------- Выбор параметров синтезирования -------------
% Выбираем кол-во ОФ используемых при синтезе (Nbl_r или 1 или др.)
Nbl_r = Nbl_r; %1; %Nbl_r;    
% При известной величине V0 ставим значение, либо в дальнейшем используется режим АФ 
V0 = V0;  
alfa0 = 0; % Ugol_snosa;
for Nugol=1:1:1
alfa = alfa0(Nugol);
 N_snos_x_bl = fix(tan(alfa*pi/180)*R_UO/dx); % Если на всех дальностях снос не изменять !!!
for Qv = 1:1:1
    clear RLI_itog
    RLI=zeros(Ndrz0,Na0);
    V=V0;
%     V=94+0.1*Qv;
    Vi(Qv) = V; 
    dx = V*Tpi;
K_otn_sr = 0;
    for Y = 1:1:Nbl_r
        if Nbl_r == 1
            R_centr_bl = R_UO; 
            Ndr = Ndrz0;
        elseif Nbl_r > 1
            R_centr_bl = Rmin+(Y*Ndr-Ndr/2)*dnr; % Наклонная дальность до центра блока в метрах
        end
        R_cb(Y)=R_centr_bl;
        % Определяем необходимую длину интервала синтезирования исходя из
        % величины razr
        Nas_bl=fix(lamb*R_centr_bl/(2*resol*dx));
        Nas_bl = fix(Nas_bl/2)*2;
        % Вычисление величины сноса в отсчётах
        if alfa==0
            N_snos_x_bl=0;
        elseif alfa~=0
%         N_snos_x_bl1=fix(a0/Na0*lamb*R_cenr_bl/2/dx^2); % Вычисление сноса в отсчётах
%         Alfa = 2.67*pi/180;
%         N_snos_x_bl = fix(tan(alfa*pi/180)*R_centr_bl/dx);
        end
        dsm = -N_snos_x_bl;                       % Требуемое Смещение ОФ
        dsm_bl(Y,Nugol) = dsm;
        % Определим максимальную кривизну фронта при R_cenr_bl, Las_max и N_snos_x
        Las_bl(Y) = Nas_bl*dx;
        x_max=Las_bl(Y)/2+abs(N_snos_x_bl)*dx;
        rt1_max_bl=sqrt(R_centr_bl^2+x_max^2)-R_centr_bl; 
        N0max(Y) = round(rt1_max_bl/dnr);
        dop_Ndr = N0max(Y); % Добавка отсчетов за счет миграции по дальности
        if dop_Ndr > Ndrz0-Y*Ndr
            dop_Ndr = Ndrz0-Y*Ndr;
        elseif dop_Ndr<0
               msg = 'Величина dop_Ndr не может быть меньше нуля';
               error(msg)
        end
        Ndr_bl = Ndr+dop_Ndr;    % Высота блока РГГ выбранного в обработку
%         rgg_bl = rgg1((Y-1)*Ndr+1:Y*Ndr+dop_Ndr,Ox*Ndx-Nas_max/2+1:(Ox+1)*Ndx+Nas_max/2);
        rgg_bl = rgg1((Y-1)*Ndr+1:Y*Ndr+dop_Ndr,:);
        % ///// Формирование ОФ по блокам дальности /////
%         Form_OF=0
        OF1_bl=zeros(1,Nas_bl);
        OF2_bl=zeros(Ndr_bl,Nas_bl);
        for i=1:1:Nas_bl
            x=(-Nas_bl/2+dsm+i-1)*dx;
            rt=sqrt(R_centr_bl^2+x^2);
            rt1=rt-R_centr_bl;
            N0_bl(i)=(fix(rt1/dnr));
            faza=-4*pi*rt/lamb;
            OF1_bl(i)=complex(cos(faza), sin(faza));
            
%             OF2_bl(N0_bl+1,i)=OF1_bl(i);
        end
        % ///// Процедура апотизации (по Хемменгу) ////////
        Apotizac = 0;
        if Apotizac == 1
            sp_OF1 = fft(OF1_bl);
%             figure
%             plot(abs(sp_OF1))
%             grid on
%             hold on
            Nai=Nas_bl;
            s=zeros(1,Nai);
            %Nsp=Nd/2*dx/ras;   % Количество отсчётов на половине ширины спектра
            Nsp=250;   % Количество отсчётов на половине ширины спектра
            Kh=0.08;
            Nh=2;
            s(1)=1;
            for n=2:1:(Nsp)
                s(n)=Kh+(1-Kh)*(cos(pi*n/Nsp/2)^Nh);
                s(Nai-n+2)=s(n);    
            end
%             plot(s*max(abs(sp_OF1)))
%             grid on
            sp_OF1_bl_Hem = sp_OF1.*s;
%             figure
%             plot(abs(sp_OF1_bl_Hem))
            OF1_bl_Hem = ifft(sp_OF1.*s);
            for i=1:1:Nas_bl
                OF2_bl(N0_bl(i)+1,i)=OF1_bl_Hem(i);
            end
        elseif Apotizac == 0
            for i=1:1:Nas_bl
                OF2_bl(N0_bl(i)+1,i)=OF1_bl(i);
            end
        else
            msg = 'Не выбран показатель апотизации';
            error(msg)
        end
        % //////////// стоп процедура апотизации ///////////////
        OF_bl=zeros(Ndr_bl,Na0);
        [Ndr_OF Na_OF]=size(OF2_bl);
        if Ndr_OF>Ndr_bl
           OF2_bl(Ndr_bl+1:end,:)=[];
%            Disp('Миграция по дальности превышает высоту блока РГГ !!!')
%            stop
        end
        if Na0/2 < Nas_bl/2+abs(dsm)
            msg = 'Не выполняется условие Na0/2 >= Nas_bl/2+dsm';
            error(msg)
        end
        OF_bl(:,Na0/2-Nas_bl/2+dsm+1:Na0/2+Nas_bl/2+dsm)=OF2_bl;
%         figure
%         h=image(real(OF_bl)*100);
%         colormap(gray); title('Реальная часть ОФ')
% ******** Визуализация и контроль правильности выбора угла сноса *********
% ****************           и кривизны фронта          *******************
% Накладываем ОФ на трек от УО и контролируем совпадение кривизны фронта
%         nuli(547,Na0)=zeros;
%         OF_bl2=[nuli;OF_bl];
%         OF_bl2(Ndr_OF+1:end,:)=[];
%         nuli2(Ndr_OF,6200)=zeros;
%         OF_bl3=[nuli2 OF_bl2];
%         OF_bl3(:,Na0+1:end)=[];
%         OF_bl3 = abs(OF_bl3);
%         clear OF2_bl OF1_bl
% %         OF_bl2=fftshift(OF_bl2,2);
%         Ris = rgg1+OF_bl3*10000000;
%         figure
%         h=image(real(Ris)*0.005);
%         colormap(gray);
%         title(['РГГ и ОФ, V = ',num2str(Vi(Qv)),' Снос = ',num2str(alfa)])
%         clear OF_bl3 OF_bl2 nuli2 nuli Ris
%         % Накладываем спектр ОФ на спектр Допл частот
%         sum_sp_rgg_bl(Na0)=0;
%         sum_sp_OF_bl(Na0)=0;
%         for n=1:1:Ndr_bl
%             rg_str=abs(fft(rgg_bl(n,:)));
%             OF_str=OF_bl(n,:);
%             sum_sp_rgg_bl=sum_sp_rgg_bl+rg_str;
%             sum_sp_OF_bl=sum_sp_OF_bl+OF_str;
%         end
%         sum_sp_OF_bl = abs(fft(sum_sp_OF_bl));
%         figure
%         plot(sum_sp_rgg_bl./max(sum_sp_rgg_bl),'b'); 
%         hold on
%         plot(sum_sp_OF_bl./max(sum_sp_OF_bl),'r'); 
%         title(['Спектр Доплер.частот РГГ и ОФ, V = ',num2str(Vi(Qv)),' Снос = ',num2str(alfa)])
%         clear sum_sp_rgg_bl sum_sp_OF_bl
% ************************************************************************
% ************************************************************************
        % Поблочный Синтез РЛИ в спектральной области
%         Sintez=0
        sp_rgg_bl = fft2(rgg_bl);
        clear rgg_bl
        % Свертка        
        sp_OF_bl = fft2(OF_bl);
        clear OF_bl
        RLI_bl=sp_rgg_bl.*conj(sp_OF_bl); 
        clear sp_rgg_bl sp_OF_bl
        CRLI_bl=ifft2(RLI_bl);
        RLI_bl=abs(CRLI_bl);
        clear CRLI_bl
%         CRLI((Y-1)*Ndr+1:Y*Ndr,:) = CRLI_bl(1:Ndr,:);
        RLI((Y-1)*Ndr+1:Y*Ndr,:) = RLI_bl(1:Ndr,:);
%         K_otn = max(max(RLI_bl(1:Ndr,:)))/std(RLI_bl(1:Ndr,:));
%         K_otn_sr = K_otn_sr+K_otn;
        clear RLI_bl RLI_bl_osr
        Cykl_y = Y
    end
    RLI=fftshift(RLI,2);    
    K_otn3(Qv,Nugol)=K_otn_sr;
%     RLI2 = flip(RLI);
%     CRLI = flip(CRLI);
    % Анализ полученного РЛИ
    min_RLI = min(min(RLI));
    max_RLI = max(max(RLI));
    K_otn1(Qv,Nugol) = std(RLI)/mean(RLI);
    K_otn2(Qv,Nugol) = max_RLI/std(std(RLI));
    % Работа с уголковыми отражателями
    Ny2 = [705 725];
    Nx2 = [2400 2700];
    UO = RLI(Ny2(1):Ny2(2),Nx2(1):Nx2(2)); % Выбираем УО на РЛИ
    % Вызов функции опр-я разрешения по УО и координат Максимума
    % [выходные данные] = name_F(входные данные);
    [razr_x(Qv,Nugol),razr_y(Qv,Nugol),Amp(Qv,Nugol),Nx02(Qv,Nugol),...
       Ny02(Qv,Nugol)] = Funct_razr_po_UO(UO,dnr,dx,Nx2,Ny2,V,alfa);
    figure
    h=image(RLI*0.0002);
%     h=image(RLI(500:900,3000:13000)*0.0001);
    title(['РЛИ, V = ',num2str(Vi(Qv)),' Снос = ',num2str(alfa)])
    colormap(gray); hold on        
%     plot([Nx02(Qv,Nugol)-1 Nx02(Qv,Nugol)+1], [Ny02(Qv,Nugol)-1 Ny02(Qv,Nugol)+1], 'r', 'LineWidth',2)
%     plot([Nx02(Qv,Nugol)-1 Nx02(Qv,Nugol)+1], [Ny02(Qv,Nugol)+1 Ny02(Qv,Nugol)-1], 'r', 'LineWidth',2)
    
% % %      %Осреднение по координам азимута и дальности
% % %     Koef2_x = fix(dnr/dx); 
% % %     RLI_osr = medfilt2(RLI,[2,Koef2_x]);
% % %     figure
% % %     h=image(RLI_osr*0.0001);
% % %     colormap(gray);
% % %     title(['РЛИ после осреднения, V = ',num2str(V),' Снос = ',num2str(alfa)])

    Cykl_V = Qv
    pause(0.3)
%     clear RLI
end
end
   
% % Осреднение РЛИ
% Mashtab = 1
% if Mashtab~=1
%    Kx=1; Ky=1;
% elseif Mashtab==1
% % Масштабирование РГГ (приводим к квадратному пикселу)
% piks=0.25;
% Kx = piks/dx;  % Коэф-т переквантования РГГ по азимуту
% Ky = dnr/piks; % Коэф-т переквантования РГГ по дальности
% sprli=fft2(RLI2); 
% Naa2 = fix(Na/Kx/2);
% Ndrz2=fix(Ndrz*Ky/2)*2;
% Nd_zeros(Ndrz2-Ndrz,Naa2*2)=zeros;
% % Урезаем спектр РЛИ по азимуту
% sp_rgg01(:,1:Naa2) = sprli(:,1:Naa2);
% sp_rgg01(:,Naa2+1:Naa2*2) = sprli(:,Na-Naa2+1:end);
% clear sprli
% % Раздвигаем спектр по наклонной дальности
% sp_rgg01 = [sp_rgg01(1:Ndrz/2,:);Nd_zeros;sp_rgg01(Ndrz/2+1:Ndrz,:)];
% % Теперь шаг по обеим координатам один и равен величине piks
% dx2=piks;
% dnr2=piks;
% CRLI025=ifft2(sp_rgg01);
% RLI025=abs(CRLI025);
% clear sp_rgg01
% figure
% h=image(RLI025*0.000025);
% title(['РЛИ после осреднения, V = ',num2str(Vi(Qv)),' Снос = ',num2str(alfa)])
% colormap(gray);    
% end




% % +++++ Построение графиков Для выбора V при АФ по УО +++++
% figure
% hrez1 = plot(Vi, razr_x); grid on
% title('Разрешение по азимуту')
% figure
% hAmp1 = plot(Vi, Amp); grid on
% title('Амплитуда УО')
% 
% figure
% hKoef1 = plot(Vi, K_otn1); grid on
% title('Коэф-т отношения 1')
% 
% figure
% hKoef1 = plot(Vi, K_otn2); grid on
% title('Коэф-т отношения 2')
% 
% figure
% hKoef1 = plot(Vi, K_otn3); grid on
% title('Коэф-т отношения 3')
% hold on
% hrez2 = plot(Vi, rezol_x2(2,:),'DisplayName','Снос = 3/4','Color','r')
% hrez3 = plot(Vi, rezol_x2(3,:),'DisplayName','Снос = 1/2','Color','g')
% hrez4 = plot(Vi, rezol_x2(4,:),'DisplayName','Снос = 1/4','Color','c')
% hrez5 = plot(Vi, rezol_x2(5,:),'DisplayName','Снос = 0','Color','m')
% legend('show')
% grid on
% xlabel('Скорость, м/с'); ylabel('Разрешение по азимуту, м')
% title('Разрешение по азимуту по УО')
% figure
% plot(Vi, rezol_y2, 'b')
% grid on
% title('Разрешение по дальности по УО2')
% xlabel('Скорость, м/с'); ylabel('Разрешение по наклонной дальности, м')
% figure
% hamp1 = plot(Vi, Amp2(1,:),'DisplayName','Снос = 1','Color','b')
% hold on
% hamp2 = plot(Vi, Amp2(2,:),'DisplayName','Снос = 3/4','Color','r')
% hamp3 = plot(Vi, Amp2(3,:),'DisplayName','Снос = 1/2','Color','g')
% hamp4 = plot(Vi, Amp2(4,:),'DisplayName','Снос = 1/4','Color','c')
% hamp5 = plot(Vi, Amp2(5,:),'DisplayName','Снос = 0','Color','m')
% legend('show')
% grid on
% xlabel('Скорость, м/с'); ylabel('Max амплитуды')
% title('Max амплитуды от УО ')
% 
% figure
% hk1 = plot(Vi, K_otn1(1,:),'DisplayName','Снос = 1','Color','b')
% hold on
% hk2 = plot(Vi, K_otn1(2,:),'DisplayName','Снос = 3/4','Color','r')
% hk3 = plot(Vi, K_otn1(3,:),'DisplayName','Снос = 1/2','Color','g')
% hk4 = plot(Vi, K_otn1(4,:),'DisplayName','Снос = 1/4','Color','c')
% hk5 = plot(Vi, K_otn1(5,:),'DisplayName','Снос = 0','Color','m')
% legend('show')
% grid on
% xlabel('Скорость, м/с'); ylabel('Коэф-т отношения')
% title('Отношение СКО к среднему')
% 
% figure
% hk1 = plot(Vi, K_otn2(1,:),'DisplayName','Снос = 1','Color','b')
% hold on
% hk2 = plot(Vi, K_otn2(2,:),'DisplayName','Снос = 3/4','Color','r')
% hk3 = plot(Vi, K_otn2(3,:),'DisplayName','Снос = 1/2','Color','g')
% hk4 = plot(Vi, K_otn2(4,:),'DisplayName','Снос = 1/4','Color','c')
% hk5 = plot(Vi, K_otn2(5,:),'DisplayName','Снос = 0','Color','m')
% legend('show')
% grid on
% xlabel('Скорость, м/с'); ylabel('Коэф-т отношения')
% title('Отношение СКО к среднему без min')
