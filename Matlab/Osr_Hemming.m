function [CRLIsr] = Osr_Hemming(Mashtab,III,dx,dnr,piks,razr_treb_x,razr_treb_y)
    
III_sp = fft2(III);
if Mashtab==1
    Koef1_r = piks/dnr; % ����-� ��������������� ��� �� ���������
    Koef1_x = piks/dx;  % ����-� ��������������� ��� �� �������

    if Koef1_x<1
       msg = '���������� ��������� ������� �� �������';
       error(msg)
    end
    [Ndf0,Naf0] = size(III);
    % ///////////// ��������������� ��� \\\\\\\\\\\\\\\\\\\\\\\\

    % ��������������� �� ���������� ���������
    if Koef1_r<1
        % ��������� ��������� ������� �� ���������
        Ndrz2=fix(Ndf0/Koef1_r/2)*2;
        Nd_zeros(Ndrz2-Ndf0,Naf0)=zeros;
        III_sp = [III_sp(1:Ndf0/2,:);Nd_zeros;III_sp(Ndf0/2+1:Ndf0,:)];
    end
    if Koef1_r>1
        % ������� ���������� ������� � ������� �� ���������
        Nr1 = fix(Ndf0/Koef1_r/4)*2;
        III_sp(Nr1+1:Ndf0-Nr1,:)=[];
    end
    % ��������������� �� ���������� ������
    if Koef1_x>1
        % ������� ���������� ������� � ������� �� �������
        Nx1 = fix(Naf0/Koef1_x/4)*2;
        III_sp(:,Nx1+1:Naf0-Nx1,:)=[];
    end
    dx2=piks; dnr2=piks;
elseif Mashtab~=1
    dx2=dx; dnr2=dnr;
end
% \\\\\\\\\\\\ ����� ��������� ��������������� /////////////
%
% ////////////////// ���������� ��� \\\\\\\\\\\\\\\\\\\\\\\\
    [Ndf,Naf] = size(III_sp);
    Koef2_r = razr_treb_y/dnr2; % ����-� ���������� ��� �� ���������
    Koef2_x = razr_treb_x/dx2;  % ����-� ���������� ��� �� �������
     % ���������� �� ��������
            VNd=(1:Ndf); % ������-������ ��� ���������� ��������� ���������
            VNa=(1:Naf);   % ������-������ ��� ���������� �������
            MF_Hem_x=zeros(1,Naf);
            MF_Hem_y=zeros(Ndf,1);
            Koef2_x = Koef2_x/2;   % ���������� ������� ���������� �� ���� ���������� �-��� ���
            Koef2_r = Koef2_r/2;   % �� ����� ����������� - ��������� ����-� ���������� 
            Nr1 = fix(Ndf/Koef2_r/4)*2;
            Nx1 = fix(Naf/Koef2_x/4)*2;
            Kh=0.08;
            Nh=2;
            % ������������ ������������ �������
            MF_Hem_x(1)=1;
            for i=2:1:Nx1
                MF_Hem_x(i)=Kh+(1-Kh)*(cos(pi*i/Nx1/2)^Nh);
                MF_Hem_x(Naf-i+2)=MF_Hem_x(i);    
            end
            MF_Hem_y(1)=1;
            for n=2:1:Nr1
                MF_Hem_y(n)=Kh+(1-Kh)*(cos(pi*n/Nr1/2)^Nh);
                MF_Hem_y(Ndf-n+2)=MF_Hem_y(n);    
            end
    %         III_sp = fft2(III);
            clear III
            % ���������� �� �������
            I_Hem = III_sp(VNd,:).*MF_Hem_x;
            clear III_sp
            % ���������� �� ��������
            I_Hem2 = I_Hem(:,VNa).*MF_Hem_y;
            clear I_Hem MF_Hem_x MF_Hem_y
            CRLIsr = ifft2(I_Hem2);
%             III_osr = abs(ifft2(I_Hem2));
% \\\\\\\\\\\\ ����� ��������� ���������� /////////////
end
