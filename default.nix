{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
    name = "TrifleBot";
    buildInputs = with pkgs; [
        pipenv
        python311
        python311Packages.alembic
        python311Packages.sqlalchemy
        python311Packages.aiomysql
        stdenv.cc.cc.lib
    ];

    # fixes libstdc++ issues and libgl.so issues
    shellHook = ''
        LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc}/lib/
    '';
}
