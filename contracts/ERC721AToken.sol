// SPDX-License-Identifier: MIT
// ERC721A Contracts v4.2.3
import "./ERC721A.sol";

pragma solidity ^0.8.4;

contract ERC721AToken is ERC721A {
    constructor(address[] memory recivers, uint256[] memory amounts)
        ERC721A("ERC721A", "A")
    {
        require(
            recivers.length == amounts.length,
            "length of recivers and amounts does not match"
        );
        for (uint256 i = 0; i < recivers.length; i++) {
            ERC721A._mintERC2309(recivers[i], amounts[i]);
        }
    }

    function mintSingle() public {
        ERC721A._mint(msg.sender, 1);
    }

    function multiMint() public {
        ERC721A._mint(msg.sender, 10);
    }

    function burnThis(uint256 tokenId) public {
        _burn(tokenId, true);
    }
}
