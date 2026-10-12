{
  # The latest stable release of nixpkgs. A tarball downloads much faster than a clone of the
  # whole repository; to update it, change the URL and get the new hash with
  # `nix-prefetch-url --unpack <url>`.
  pkgs ? import (builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/refs/tags/26.05.tar.gz";
    sha256 = "0am8xx09fx5yf2p0wb001v0jx1g5hrfb76h4r37xph378jgk7pcr";
  }) {},
  dev ? true,
}:
let 
  py311 = pkgs.python311;
  poetryExtras = if dev then ["dev"] else [];
  poetryInstallExtras = (
    if poetryExtras == [] then ""
    else pkgs.lib.concatStrings [ " --with=" (pkgs.lib.concatStringsSep "," poetryExtras) ]
  );
  # The nox sessions install their dependencies with `poetry export`, which Poetry 2 leaves to
  # a plugin; Poetry finds a plugin only when it is built with it.
  poetryWithPlugins = if dev then pkgs.poetry.withPlugins (ps: [ ps.poetry-plugin-export ]) else pkgs.poetry;
in
pkgs.mkShell {
  name = "spotfishing-env";
  buildInputs = with pkgs; [
    pkgs.zlib
    pkgs.stdenv.cc.cc.lib
    poetryWithPlugins
    py311
    python312
  ] ++ (if dev then [
    # The pyright package from PyPI runs on Node.js; providing it here saves a download.
    pkgs.nodejs
  ] else []);
  shellHook = ''
    # To get this working on the lab machine, we need to modify Poetry's keyring interaction:
    # https://stackoverflow.com/questions/74438817/poetry-failed-to-unlock-the-collection
    # https://github.com/python-poetry/poetry/issues/1917
    export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
    poetry env use "${py311}/bin/python"
    export LD_LIBRARY_PATH="${pkgs.zlib}/lib:${pkgs.stdenv.cc.cc.lib}/lib"
    poetry sync -vv${poetryInstallExtras}
    source "$(poetry env info --path)/bin/activate"
  '';
}
