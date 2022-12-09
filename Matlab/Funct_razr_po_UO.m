function [razr_x,razr_y,Amp,Nx02,Ny02]...
    = Funct_razr_po_UO(UO,dnr,dx,Nx2,Ny2,V,alfa)
    
    [n i] = size(UO);
    Lin07(1:i)=0.7;
    [A1 X_max] = max(max(UO));
	[A2 Y_max] = max(UO(:,X_max));
    str_UO = UO(Y_max,:);
    stolb_UO = UO(:,X_max);
    if A1~=A2
        msg = 'Error Amp.';
        error(msg)
    end
    Amp = A1;
    str_zeros = str_UO;
    for z1=1:1:i
        if str_UO(z1)<0.7*Amp
        str_zeros(z1) = 0;
        end
    end
    razr_x = nnz(str_zeros)*dx;
    
    stolb_zeros = stolb_UO;
    for z2=1:1:n
        if stolb_UO(z2)<0.7*Amp
        stolb_zeros(z2) = 0;
        end
    end
    razr_y = nnz(stolb_zeros)*dnr;
    Ny02 = Y_max+Ny2(1);
    Nx02 = X_max+Nx2(1);
    % Вывод РЛИ УО и его сечения по азимуту
    Kamp=min(min(UO));
    Kamp2=max(max(UO))-min(min(UO));
%     figure
    subplot(1,2,2);
    image(UO,'CDataMapping','scaled')
    colormap(gray);
    title(['РЛИ УО, V = ',num2str(V),' Снос = ',num2str(alfa)])
    hold on
    plot([X_max-1 X_max+1], [Y_max-1 Y_max+1], 'r', 'LineWidth',2)
    plot([X_max-1 X_max+1], [Y_max+1 Y_max-1], 'r', 'LineWidth',2)
    subplot(1,2,1);
    plot(UO(Y_max,:)/max(UO(Y_max,:))); grid on; hold on
    plot(Lin07,'r')
    text(10,0.75,['razr_x=',num2str(razr_x)])
    text(10,0.65,['razr_y=',num2str(razr_y)])
    title(['Сечение УО по азимуту, V = ',num2str(V),' Снос = ',num2str(alfa)])
end