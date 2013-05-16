#include <QApplication>
#include <QPushButton>
#include <QTranslator>
#include <QDebug>

#include <iostream>

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    if (argc < 3) {
      std::cerr << "Usage: translateme QM_DIR LOCALE" << std::endl;
     return 1;
    }

    QString qmDir(argv[1]);
    QString locale(argv[2]);
    QString fileName = QString("helloqt_") + locale;

    QTranslator translator;
    translator.load(fileName, qmDir);
    app.installTranslator(&translator);

    QString hello = QApplication::tr("Hello world!");
    std::cout << hello.toUtf8().data();

    return 0;
}
