% function [�������� ������] = name_funct(������� ������)
function [N_snos_sr, Ugol_snosa, a0] = Funct_opredel_ugla_snosa(rgg1,Rsr,dx,lamb)
[Ndrz0 Na0]=size(rgg1)
% +++++++ ��������� �� ��� ���� +++++++++++
rg_sum=zeros(1,Na0); 
rg_sum=sum(rgg1);
sr_rg_sum = mean(rg_sum);
rg_sum=rg_sum-sr_rg_sum; % ������� ���������� ������������
% figure
% plot(real(rg_sum))
srgg1=fft(rg_sum);% ���������� ����. �������
Asrgg1=abs(srgg1);% ������ �������
% figure
% plot(Asrgg1);
% ����������� ����. �������
Argg1=ifft(Asrgg1);
Argg1(10:end-10)=0;
srgg1=fft(Argg1);
% figure
% plot(fftshift(abs(srgg1)));
% ����������� �������� �������
sm=max(abs(srgg1))*0.9; % ������� ����������
for i=1:1:Na0 
    if (abs(srgg1(i))>=sm)
    srgg1(i)=1;
    else
    srgg1(i)=0;    
    end    
end  
for i=1:1:(Na0-1) 
    if (srgg1(i)<srgg1(i+1))
    a1=i;
    end
    if (srgg1(i)>srgg1(i+1))
    a2=i;
    end
end
    if (a1>a2)
        a2=a2+Na0;
    end
a0=(a1+a2)/2;
    if (a0>Na0/2)
        a0=a0-Na0;        
    end
% ����������� ����������� ��������� ��������� �� �����������
% R_UO = 3995;
% N_UO = 1713;
% Rmin = R_UO-(N_UO-1)*dnr;
% Rmax = Rmin+Ndrz*dnr;
% Rsr = (Rmax+Rmin)/2;

N_snos_x=fix(a0/Na0*lamb*Rsr/2/dx^2) % ���������� ����� � �������� ��� Rsr
dsm0 = -N_snos_x;                       % ��������� �������� ��
alfa=atand(N_snos_x*dx/Rsr)           % ���������� ����� � ��������
Ugol_snosa=alfa;
N_snos_sr = N_snos_x;
end